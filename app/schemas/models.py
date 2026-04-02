from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class GalleryBase(BaseModel):
    title: str
    image_url: str
    public_id: str  # Cloudinary public ID for deletion

class GalleryCreate(GalleryBase):
    pass

class GalleryUpdate(BaseModel):
    title: Optional[str] = None
    image_url: Optional[str] = None
    public_id: Optional[str] = None

class GalleryInDB(GalleryBase):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)

class ServiceBase(BaseModel):
    heading: str
    description: str
    long_description: Optional[str] = None
    guidelines: List[str] = []
    image_url: str
    public_id: str

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    heading: Optional[str] = None
    description: Optional[str] = None
    long_description: Optional[str] = None
    guidelines: Optional[List[str]] = None
    image_url: Optional[str] = None
    public_id: Optional[str] = None

class ServiceInDB(ServiceBase):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)

class BlogBase(BaseModel):
    title: str
    excerpt: str
    content: str
    category: str
    image_url: str
    public_id: str

class BlogCreate(BlogBase):
    pass

class BlogUpdate(BaseModel):
    title: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    public_id: Optional[str] = None

class BlogInDB(BlogBase):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)

class ProjectBase(BaseModel):
    title: str
    sector: str
    location: str
    description: str
    image_url: str
    public_id: str

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    sector: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    public_id: Optional[str] = None

class ProjectInDB(ProjectBase):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)

class VacancyBase(BaseModel):
    title: str
    department: str
    location: str
    type: str # Full-time, Part-time, Contract
    description: str
    requirements: List[str] = []

class VacancyCreate(VacancyBase):
    pass

class VacancyUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = None

class VacancyInDB(VacancyBase):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)

class JobApplicationBase(BaseModel):
    job_id: str
    job_title: str
    name: str
    qualification: str
    mobile: str
    email: str
    address: str
    pincode: str

class JobApplicationCreate(JobApplicationBase):
    pass

class JobApplicationInDB(JobApplicationBase):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)
