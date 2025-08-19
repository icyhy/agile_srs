from marshmallow import Schema, fields, validate


class RequirementCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(required=True, validate=validate.Length(min=1))


class RequirementInviteSchema(Schema):
    email = fields.Email(required=True)


class RequirementContentSchema(Schema):
    content_type = fields.Str(required=True, validate=validate.OneOf(['text', 'image', 'audio']))
    content = fields.Str(required=False)
    file = fields.Raw(required=False)

    # 验证至少提供content或file之一
    def validate(self, data, **kwargs):
        if not data.get('content') and not data.get('file'):
            raise validate.ValidationError('Either content or file must be provided.')
        return data


class RequirementSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    creator_id = fields.Int()
    status = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()