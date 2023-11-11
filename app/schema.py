from pydantic import BaseModel, field_validator


class NotificationIn(BaseModel):
    user_id: str
    key: str
    target_id: str | None = None
    data: dict | None = None

    @field_validator('user_id')
    @classmethod
    def user_id_must_equal_len_24(cls, user_id: str) -> str:
        assert len(user_id) == 24, 'length string user_id must be 24'
        return user_id

    @field_validator('target_id')
    @classmethod
    def target_id_must_equal_len_24(cls, target_id: str) -> str:
        assert len(target_id) == 24, 'length string target_id must be 24'
        return target_id

    @field_validator('key')
    @classmethod
    def key_must_equal_params(cls, key: str) -> str:
        assert key in ('registration', 'new_message', 'new_post',
                       'new_login'), 'key must be registration, new_message, new_post or new_login'
        return key

