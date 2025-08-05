"""
AWS Rekognition based face recognition module - Optional component
This module can be imported and used when AWS credentials are available
"""

import cv2
import numpy as np
import boto3
import base64
import json
import os
from typing import Optional, List, Tuple, Dict, Any
from botocore.exceptions import ClientError, NoCredentialsError

class AWSFaceRecognitionModule:
    """AWS Rekognition based face recognition system - Optional module"""
    
    def __init__(self, region_name: str = 'us-east-1'):
        """
        Initialize AWS Rekognition client
        
        Args:
            region_name: AWS region for Rekognition service
        """
        try:
            self.rekognition = boto3.client('rekognition', region_name=region_name)
            self.collection_id = 'gesture-control-faces'
            self.region_name = region_name
            
            # Create collection if it doesn't exist
            self._create_collection_if_not_exists()
            
            print(f"AWS Rekognition initialized successfully in region: {region_name}")
            
        except NoCredentialsError:
            print("ERROR: AWS credentials not found. Please configure AWS credentials.")
            raise
        except Exception as e:
            print(f"Error initializing AWS Rekognition: {e}")
            raise
    
    def _create_collection_if_not_exists(self):
        """Create face collection if it doesn't exist"""
        try:
            # Try to describe the collection
            self.rekognition.describe_collection(CollectionId=self.collection_id)
            print(f"Using existing collection: {self.collection_id}")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # Collection doesn't exist, create it
                try:
                    response = self.rekognition.create_collection(CollectionId=self.collection_id)
                    print(f"Created new collection: {self.collection_id}")
                    print(f"Collection ARN: {response.get('CollectionArn', 'N/A')}")
                except ClientError as create_error:
                    print(f"Error creating collection: {create_error}")
                    raise
            else:
                print(f"Error checking collection: {e}")
                raise
    
    def _image_to_bytes(self, image: np.ndarray) -> bytes:
        """Convert OpenCV image to bytes for AWS API"""
        try:
            # Encode image as JPEG
            _, buffer = cv2.imencode('.jpg', image)
            return buffer.tobytes()
        except Exception as e:
            print(f"Error converting image to bytes: {e}")
            raise
    
    def register_face(self, image: np.ndarray, user_id: str) -> bool:
        """
        Register a new face for a user using AWS Rekognition
        
        Args:
            image: OpenCV image (BGR format)
            user_id: Unique identifier for the user
            
        Returns:
            bool: True if registration successful, False otherwise
        """
        try:
            # Validate image quality first
            is_valid, message = self.validate_image_quality(image)
            if not is_valid:
                print(f"Image validation failed: {message}")
                return False
            
            # Convert image to bytes
            image_bytes = self._image_to_bytes(image)
            
            # Index face in collection
            response = self.rekognition.index_faces(
                CollectionId=self.collection_id,
                Image={'Bytes': image_bytes},
                ExternalImageId=user_id,
                MaxFaces=1,
                QualityFilter='AUTO',
                DetectionAttributes=['ALL']
            )
            
            if response['FaceRecords']:
                face_record = response['FaceRecords'][0]
                face_id = face_record['Face']['FaceId']
                confidence = face_record['Face']['Confidence']
                
                print(f"Face registered successfully for user: {user_id}")
                print(f"Face ID: {face_id}")
                print(f"Detection confidence: {confidence:.2f}%")
                return True
            else:
                print("No face detected in the image")
                return False
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'InvalidParameterException':
                print("Invalid image format or quality")
            elif error_code == 'InvalidImageFormatException':
                print("Unsupported image format")
            else:
                print(f"AWS Rekognition error: {e}")
            return False
        except Exception as e:
            print(f"Error registering face: {e}")
            return False
    
    def authenticate_face(self, image: np.ndarray, user_id: str) -> bool:
        """
        Authenticate a user using face recognition with AWS Rekognition
        
        Args:
            image: OpenCV image (BGR format)
            user_id: User ID to authenticate against
            
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Convert image to bytes
            image_bytes = self._image_to_bytes(image)
            
            # Search for faces in the collection
            response = self.rekognition.search_faces_by_image(
                CollectionId=self.collection_id,
                Image={'Bytes': image_bytes},
                MaxFaces=1,
                FaceMatchThreshold=80.0  # 80% confidence threshold
            )
            
            if response['FaceMatches']:
                for match in response['FaceMatches']:
                    # Get face details
                    face_id = match['Face']['FaceId']
                    confidence = match['Similarity']
                    
                    # Get external image ID (user_id) for this face
                    face_response = self.rekognition.list_faces(
                        CollectionId=self.collection_id,
                        MaxResults=1000  # Get all faces to find the matching one
                    )
                    
                    for face in face_response['Faces']:
                        if face['FaceId'] == face_id and face['ExternalImageId'] == user_id:
                            print(f"Face authentication successful for user: {user_id}")
                            print(f"Confidence: {confidence:.2f}%")
                            return True
                
                print(f"Face detected but doesn't match user: {user_id}")
                return False
            else:
                print("No matching faces found")
                return False
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'InvalidParameterException':
                print("No face detected in the authentication image")
            else:
                print(f"AWS Rekognition error: {e}")
            return False
        except Exception as e:
            print(f"Error during face authentication: {e}")
            return False
    
    def validate_image_quality(self, image: np.ndarray) -> Tuple[bool, str]:
        """
        Validate image quality for face registration
        
        Args:
            image: OpenCV image to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            # Check image size
            height, width = image.shape[:2]
            if width < 200 or height < 200:
                return False, "Image too small. Minimum size is 200x200 pixels"
            
            # Check brightness
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            
            if brightness < 50:
                return False, "Image too dark. Please ensure good lighting"
            elif brightness > 200:
                return False, "Image too bright. Please reduce lighting"
            
            # Check for blur
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            if laplacian_var < 100:
                return False, "Image too blurry. Please take a clearer photo"
            
            return True, "Image quality is good"
            
        except Exception as e:
            return False, f"Error validating image: {e}"

def get_aws_face_module():
    """
    Factory function to get AWS face recognition module if available
    
    Returns:
        AWSFaceRecognitionModule instance or None if AWS not available
    """
    try:
        return AWSFaceRecognitionModule()
    except Exception as e:
        print(f"AWS Face Recognition not available: {e}")
        return None