from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator, ConfigDict



MIN_WORKING_AGE = 18
MAX_WORKING_AGE = 65

class Address(BaseModel):
    city: str = Field(..., min_length=2)
    street: str = Field(..., min_length=3)
    house_number: int = Field(..., gt=0)

class User(BaseModel):
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.strftime("%d-%m-%Y %H:%M")
        }
    )
    name: str = Field(...,
                      min_length=2,
                      description="The name of the user")
    age: int = Field(...,
                      gt=0,
                      le=120,
                      description="Age must be between 0 and 120 years")
    email: EmailStr
    is_employed: bool = Field(default=False, description="Whether the user is employed")
    address: Address
    signup_ts: datetime = Field(default_factory=datetime.now)


    @field_validator("name")
    @classmethod
    def check_name(cls, text: str):
        if not text.isalpha():
            raise ValueError ("Name must contain only letters")
        return text

    @model_validator(mode="after")
    def check_employment(self):
        if self.is_employed and not (MIN_WORKING_AGE <= self.age <= MAX_WORKING_AGE):
            raise ValueError(
                f"User cannot be employed at age {self.age}. "
                f"Age must be between {MIN_WORKING_AGE} and {MAX_WORKING_AGE}"
            )
        return self