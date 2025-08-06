# WebSocket 멀티 클라이언트 라우팅 아키텍처

## 개요
여러 Desktop App에서 동시에 AWS 백엔드로 요청을 보낼 때, 각 앱이 본인의 요청에 대한 LLM 응답을 정확히 받을 수 있도록 하는 WebSocket 기반 아키텍처입니다.

## 아키텍처 구성요소

### 1. 클라이언트 (Desktop App)
- Python 기반 Desktop Application
- WebSocket 연결을 통한 실시간 통신
- 고유 Request ID 생성 및 관리

### 2. AWS 백엔드 서비스
- **API Gateway WebSocket**: 실시간 양방향 통신
- **DynamoDB**: 연결 상태 및 세션 관리
- **Lambda Functions**: 비즈니스 로직 처리
- **Amazon Bedrock**: LLM 처리
- **Aurora PostgreSQL**: 사용자 데이터 및 대화 이력

## 핵심 라우팅 메커니즘

### Connection 관리 (DynamoDB 테이블)
```python
# Connection 테이블 스키마
{
    "connectionId": "L0S9aeCap5sA92b=",     # Primary Key (API Gateway 제공)
    "userId": "user_001",                   # 사용자 ID  
    "sessionId": "session_abc123",          # 세션 ID
    "connectedAt": "2025-01-01T00:00:00Z",  # 연결 시간
    "lastActivity": "2025-01-01T00:05:00Z", # 마지막 활동
    "status": "active"                      # 연결 상태
}
```

### Request-Response Correlation 패턴
```python
# Desktop App에서 요청 시
request = {
    "action": "sendMessage",
    "requestId": str(uuid4()),              # 고유 요청 ID
    "userId": "user_001", 
    "message": "사용자 질문",
    "timestamp": datetime.utcnow().isoformat()
}

# Lambda에서 응답 시
response = {
    "action": "messageResponse", 
    "requestId": request["requestId"],      # 같은 요청 ID로 매칭
    "response": "LLM 생성 답변",
    "status": "completed"
}
```

## Lambda 함수 역할 분담

### 1. Connection Manager Lambda
**역할:**
- WebSocket 연결/해제 처리
- DynamoDB에 연결 정보 저장/삭제
- 연결 상태 모니터링

**이벤트 핸들러:**
```python
def lambda_handler(event, context):
    connection_id = event['requestContext']['connectionId']
    route_key = event['requestContext']['routeKey']
    
    if route_key == '$connect':
        # 새로운 연결 등록
        save_connection(connection_id, event)
    elif route_key == '$disconnect':
        # 연결 정리
        remove_connection(connection_id)
    
    return {'statusCode': 200}
```

### 2. Chat Processor Lambda  
**역할:**
- 메시지 요청 처리
- Bedrock LLM 호출
- 응답을 올바른 연결로 라우팅

**처리 로직:**
```python
def process_chat_message(event, context):
    body = json.loads(event['body'])
    connection_id = event['requestContext']['connectionId']
    request_id = body.get('requestId')
    
    # 1. LLM 처리
    llm_response = call_bedrock_llm(body['message'])
    
    # 2. 대화 이력 저장
    save_chat_history(body['userId'], body['message'], llm_response)
    
    # 3. 응답을 특정 클라이언트에게 전송
    response = {
        "action": "messageResponse",
        "requestId": request_id,
        "response": llm_response,
        "status": "completed"
    }
    
    send_to_connection(connection_id, response)
```

### 3. 메시지 라우팅 함수
```python
import boto3
import json

def send_to_connection(connection_id, data):
    """특정 클라이언트에게 메시지 전송"""
    gateway_client = boto3.client(
        'apigatewaymanagementapi',
        endpoint_url=f"https://{api_id}.execute-api.{region}.amazonaws.com/{stage}"
    )
    
    try:
        gateway_client.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(data)
        )
    except gateway_client.exceptions.GoneException:
        # 연결이 끊어진 경우 정리
        remove_connection(connection_id)
```

## Desktop App 구현 예시

### WebSocket 연결 및 메시지 처리
```python
import asyncio
import websockets
import json
import uuid
from datetime import datetime

class DesktopApp:
    def __init__(self, user_id):
        self.user_id = user_id
        self.websocket = None
        self.pending_requests = {}  # 요청 ID별 콜백 저장
        
    async def connect(self):
        """WebSocket 서버에 연결"""
        uri = "wss://your-api-gateway-websocket-url"
        self.websocket = await websockets.connect(uri)
        
        # 메시지 수신 리스너 시작
        asyncio.create_task(self.listen_messages())
    
    async def send_message(self, message):
        """메시지 전송"""
        request_id = str(uuid.uuid4())
        
        request = {
            "action": "sendMessage",
            "requestId": request_id,
            "userId": self.user_id,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # 요청 전송
        await self.websocket.send(json.dumps(request))
        
        # 응답 대기를 위한 Future 생성
        future = asyncio.Future()
        self.pending_requests[request_id] = future
        
        # 응답 반환
        return await future
    
    async def listen_messages(self):
        """서버로부터 메시지 수신"""
        async for message in self.websocket:
            data = json.loads(message)
            
            if data.get('action') == 'messageResponse':
                request_id = data.get('requestId')
                
                # 대기 중인 요청에 응답 전달
                if request_id in self.pending_requests:
                    future = self.pending_requests.pop(request_id)
                    future.set_result(data['response'])

# 사용 예시
async def main():
    app = DesktopApp("user_001")
    await app.connect()
    
    # 메시지 전송 및 응답 받기
    response = await app.send_message("안녕하세요, LLM!")
    print(f"LLM 응답: {response}")

if __name__ == "__main__":
    asyncio.run(main())
```

## API Gateway WebSocket 설정

### 라우트 구성
- `$connect`: 연결 시 호출
- `$disconnect`: 연결 해제 시 호출  
- `sendMessage`: 메시지 전송 시 호출

### CloudFormation 템플릿 예시
```yaml
Resources:
  WebSocketApi:
    Type: AWS::ApiGatewayV2::Api
    Properties:
      Name: ChatWebSocketApi
      ProtocolType: WEBSOCKET
      RouteSelectionExpression: "$request.body.action"
      
  ConnectRoute:
    Type: AWS::ApiGatewayV2::Route
    Properties:
      ApiId: !Ref WebSocketApi
      RouteKey: $connect
      Target: !Sub "integrations/${ConnectIntegration}"
      
  DisconnectRoute:
    Type: AWS::ApiGatewayV2::Route  
    Properties:
      ApiId: !Ref WebSocketApi
      RouteKey: $disconnect
      Target: !Sub "integrations/${DisconnectIntegration}"
      
  SendMessageRoute:
    Type: AWS::ApiGatewayV2::Route
    Properties:
      ApiId: !Ref WebSocketApi
      RouteKey: sendMessage
      Target: !Sub "integrations/${SendMessageIntegration}"
```

## 장점 및 특징

### ✅ 장점
- **정확한 라우팅**: Connection ID로 정확한 클라이언트 식별
- **확장성**: 수천 개의 동시 연결 지원
- **실시간성**: WebSocket으로 즉시 응답 전달
- **상태 관리**: DynamoDB에서 연결 상태 추적
- **장애 복구**: 연결 끊김 감지 및 재연결 지원

### 🎯 핵심 특징
- Request ID 기반 요청-응답 매칭
- Connection ID 기반 클라이언트 라우팅
- 세션 상태 영속성
- 비동기 메시지 처리

## 추가 고려사항

### 1. Request Timeout 처리
```python
# 요청 타임아웃 설정 (30초)
TIMEOUT = 30

async def send_message_with_timeout(self, message):
    try:
        return await asyncio.wait_for(
            self.send_message(message), 
            timeout=TIMEOUT
        )
    except asyncio.TimeoutError:
        return {"error": "Request timeout"}
```

### 2. Connection Cleanup
```python
def cleanup_stale_connections():
    """오래된 연결 정리"""
    current_time = datetime.utcnow()
    threshold = current_time - timedelta(hours=1)
    
    # 1시간 이상 비활성 연결 정리
    stale_connections = get_stale_connections(threshold)
    for conn in stale_connections:
        remove_connection(conn['connectionId'])
```

### 3. Rate Limiting
```python
def check_rate_limit(user_id):
    """사용자별 요청 제한 확인"""
    current_minute = datetime.utcnow().replace(second=0, microsecond=0)
    
    # 분당 10개 요청 제한
    request_count = get_user_request_count(user_id, current_minute)
    return request_count < 10
```

### 4. Message Ordering (FIFO 큐 사용)
```python
# SQS FIFO 큐로 메시지 순서 보장
def send_to_fifo_queue(message, user_id):
    sqs.send_message(
        QueueUrl=fifo_queue_url,
        MessageBody=json.dumps(message),
        MessageGroupId=user_id,  # 사용자별 그룹
        MessageDeduplicationId=str(uuid.uuid4())
    )
```

## 비용 최적화

### 예상 비용 구조
- **API Gateway WebSocket**: 연결 시간 + 메시지 수 기준
- **Lambda**: 실행 시간 + 메모리 사용량 기준  
- **DynamoDB**: 읽기/쓰기 요청 단위 기준
- **Bedrock**: 토큰 사용량 기준

### 최적화 방안
- Connection pooling으로 연결 재사용
- Lambda 함수 최적화 (메모리, 실행시간)
- DynamoDB On-Demand 모드 사용
- 불필요한 연결 자동 정리

이 아키텍처를 통해 여러 Desktop App이 동시에 LLM 서비스를 사용하면서도 각자의 요청에 정확한 응답을 받을 수 있습니다.