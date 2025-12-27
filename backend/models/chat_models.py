"""
Chat Models for MarketMatic Smart Assistant
Database models for chat sessions and messages
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

class ChatSession(BaseModel):
    """
    Represents a customer chat session
    """
    session_id: str = Field(..., description="Unique session identifier")
    service_id: str = Field(..., description="Service ID this session belongs to")
    user_name: str = Field(default="Guest", description="Customer name or identifier")
    status: str = Field(default="active", description="Session status: active, ended, transferred")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = Field(default=0, description="Total messages in this session")
    language_preference: str = Field(default="en", description="Detected customer language preference")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional session data")
    
    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

class ChatMessage(BaseModel):
    """
    Represents a single chat message
    """
    message_id: Optional[str] = Field(default=None, description="Unique message identifier")
    session_id: str = Field(..., description="Session this message belongs to")
    service_id: str = Field(..., description="Service ID")
    user_name: str = Field(default="Guest", description="Sender name")
    message: str = Field(..., description="Message content")
    sender: str = Field(..., description="Sender type: user, bot, admin")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Language and NLP data
    language: str = Field(default="en", description="Detected language: en, si, ta, mixed")
    intent: str = Field(default="general", description="Classified intent")
    confidence: float = Field(default=0.0, description="Intent classification confidence")
    
    # Context and AI data
    context_used: Optional[str] = Field(default=None, description="Context used for AI response")
    ai_model: Optional[str] = Field(default=None, description="AI model used for response")
    processing_time: Optional[float] = Field(default=None, description="Response generation time")
    
    # Feedback and quality
    feedback_rating: Optional[int] = Field(default=None, description="User feedback rating 1-5")
    feedback_comment: Optional[str] = Field(default=None, description="User feedback comment")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional message data")
    
    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

class ConversationContext(BaseModel):
    """
    Represents conversation context for AI processing
    """
    session_id: str = Field(..., description="Session identifier")
    recent_messages: List[Dict[str, str]] = Field(default_factory=list, description="Recent message history")
    current_intent: str = Field(default="general", description="Current conversation intent")
    language_preference: str = Field(default="en", description="Customer language preference")
    customer_data: Dict[str, Any] = Field(default_factory=dict, description="Customer context data")
    business_context: Dict[str, Any] = Field(default_factory=dict, description="Business-specific context")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ChatAnalytics(BaseModel):
    """
    Analytics data for chat performance
    """
    service_id: str = Field(..., description="Service identifier")
    date: datetime = Field(default_factory=datetime.utcnow)
    
    # Volume metrics
    total_messages: int = Field(default=0, description="Total messages processed")
    total_sessions: int = Field(default=0, description="Total chat sessions")
    unique_users: int = Field(default=0, description="Unique users served")
    
    # Performance metrics
    average_response_time: float = Field(default=0.0, description="Average AI response time")
    resolution_rate: float = Field(default=0.0, description="Query resolution rate")
    escalation_rate: float = Field(default=0.0, description="Human escalation rate")
    
    # Language and intent metrics
    language_distribution: Dict[str, int] = Field(default_factory=dict, description="Language usage distribution")
    intent_distribution: Dict[str, int] = Field(default_factory=dict, description="Intent classification distribution")
    
    # Customer satisfaction
    average_rating: float = Field(default=0.0, description="Average customer rating")
    feedback_count: int = Field(default=0, description="Total feedback responses")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class EscalationRequest(BaseModel):
    """
    Human escalation request
    """
    escalation_id: str = Field(..., description="Unique escalation identifier")
    session_id: str = Field(..., description="Chat session being escalated")
    service_id: str = Field(..., description="Service identifier")
    user_name: str = Field(default="Guest", description="Customer name")
    reason: str = Field(..., description="Escalation reason")
    priority: str = Field(default="normal", description="Priority: low, normal, high, urgent")
    status: str = Field(default="pending", description="Status: pending, assigned, resolved")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_to: Optional[str] = Field(default=None, description="Admin user assigned to handle")
    resolved_at: Optional[datetime] = Field(default=None, description="Resolution timestamp")
    notes: Optional[str] = Field(default=None, description="Admin notes")
    
    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

# MongoDB Collection Schemas for indexing and validation

CHAT_SESSIONS_SCHEMA = {
    "bsonType": "object",
    "required": ["session_id", "service_id"],
    "properties": {
        "session_id": {"bsonType": "string"},
        "service_id": {"bsonType": "string"},
        "user_name": {"bsonType": "string"},
        "status": {"enum": ["active", "ended", "transferred"]},
        "created_at": {"bsonType": "date"},
        "last_activity": {"bsonType": "date"},
        "message_count": {"bsonType": "int"},
        "language_preference": {"enum": ["en", "si", "ta", "mixed"]},
        "metadata": {"bsonType": "object"}
    }
}

CHAT_MESSAGES_SCHEMA = {
    "bsonType": "object",
    "required": ["session_id", "service_id", "message", "sender"],
    "properties": {
        "session_id": {"bsonType": "string"},
        "service_id": {"bsonType": "string"},
        "user_name": {"bsonType": "string"},
        "message": {"bsonType": "string"},
        "sender": {"enum": ["user", "bot", "admin"]},
        "timestamp": {"bsonType": "date"},
        "language": {"enum": ["en", "si", "ta", "mixed"]},
        "intent": {"bsonType": "string"},
        "confidence": {"bsonType": "double"},
        "context_used": {"bsonType": "string"},
        "ai_model": {"bsonType": "string"},
        "processing_time": {"bsonType": "double"},
        "feedback_rating": {"bsonType": "int", "minimum": 1, "maximum": 5},
        "feedback_comment": {"bsonType": "string"},
        "metadata": {"bsonType": "object"}
    }
}

ESCALATION_REQUESTS_SCHEMA = {
    "bsonType": "object",
    "required": ["escalation_id", "session_id", "service_id", "reason"],
    "properties": {
        "escalation_id": {"bsonType": "string"},
        "session_id": {"bsonType": "string"},
        "service_id": {"bsonType": "string"},
        "user_name": {"bsonType": "string"},
        "reason": {"bsonType": "string"},
        "priority": {"enum": ["low", "normal", "high", "urgent"]},
        "status": {"enum": ["pending", "assigned", "resolved"]},
        "created_at": {"bsonType": "date"},
        "assigned_to": {"bsonType": "string"},
        "resolved_at": {"bsonType": "date"},
        "notes": {"bsonType": "string"}
    }
}

# Database indexes for performance
def create_chat_indexes(db):
    """
    Create database indexes for chat collections
    """
    # Chat sessions indexes
    db.chat_sessions.create_index([
        ("service_id", 1),
        ("session_id", 1)
    ], unique=True)
    db.chat_sessions.create_index([("service_id", 1), ("last_activity", -1)])
    db.chat_sessions.create_index([("status", 1)])
    
    # Chat messages indexes
    db.chat_messages.create_index([
        ("service_id", 1),
        ("session_id", 1),
        ("timestamp", 1)
    ])
    db.chat_messages.create_index([("service_id", 1), ("timestamp", -1)])
    db.chat_messages.create_index([("intent", 1)])
    db.chat_messages.create_index([("language", 1)])
    db.chat_messages.create_index([("sender", 1)])
    
    # Escalation requests indexes
    db.escalation_requests.create_index([("service_id", 1), ("status", 1)])
    db.escalation_requests.create_index([("assigned_to", 1), ("status", 1)])
    db.escalation_requests.create_index([("created_at", -1)])
    
    print("✅ Chat database indexes created successfully")