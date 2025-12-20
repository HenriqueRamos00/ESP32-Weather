from pydantic import BaseModel, ConfigDict, Field

class SettingBase(BaseModel):
    key: str
    value: str
    description: str | None = None

class SettingCreate(SettingBase):
    pass

class SettingUpdate(BaseModel):
    value: str

class Setting(SettingBase):
    class Config:
        from_attributes = True

class SettingInDB(SettingBase):
    model_config = ConfigDict(from_attributes=True)

    pass