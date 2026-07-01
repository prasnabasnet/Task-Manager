from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from apps.users.serializers import UserDetailSerializer
from apps.comments.mention_parser import parse_mentions
from .models import Comment

class ReplySerializer(serializers.ModelSerializer):
    author = UserDetailSerializer(read_only=True)
    mentions = UserDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'author', 'body', 'mentions', 'parent', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'mentions', 'created_at', 'updated_at']


class CommentSerializer(serializers.ModelSerializer):
    # Inputs for assigning comments to a Project or Task
    target_type = serializers.ChoiceField(choices=['project', 'task'], write_only=True, required=False)
    target_id = serializers.IntegerField(write_only=True, required=False)
    
    author = UserDetailSerializer(read_only=True)
    mentions = UserDetailSerializer(many=True, read_only=True)
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'author', 'body', 'mentions', 'parent', 'replies',
            'target_type', 'target_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'mentions']

    def validate_body(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("Comment body cannot be empty.")
        if len(value) > 5000:
            raise serializers.ValidationError("Comment body cannot exceed 5000 characters.")
        return value

    def validate(self, data):
        # On update, skip target validation as the target is already established on the existing comment
        if self.instance is not None:
            return data

        parent = data.get('parent')
        target_type = data.get('target_type')
        target_id = data.get('target_id')

        # Scenario A: It's a new root comment
        if not parent:
            if not target_type or not target_id:
                raise serializers.ValidationError(
                    {"detail": "Root comments must include both 'target_type' and 'target_id'."}
                )
            
            # Match the target_type string to your exact django app label
            app_label = 'projects' if target_type == 'project' else 'tasks'
            try:
                ct = ContentType.objects.get(app_label=app_label, model=target_type)
            except ContentType.DoesNotExist:
                raise serializers.ValidationError({"target_type": "Invalid comment target type."})

            # Check if that project/task row actually exists
            model_class = ct.model_class()
            if not model_class.objects.filter(id=target_id).exists():
                raise serializers.ValidationError({"target_id": f"No {target_type} found with ID {target_id}."})

            # Cache the verified layout for perform_create
            data['content_type'] = ct

        # Scenario B: It's a reply to an existing comment
        else:
            if target_type or target_id:
                raise serializers.ValidationError(
                    {"detail": "Replies automatically inherit their target. Do not provide target_type or target_id."}
                )
            
            # Prevent replying to a reply (keeping it clean and flat)
            if parent.parent is not None:
                raise serializers.ValidationError({"parent": "You cannot reply to a reply. Only 1-level deep threading allowed."})

            # Inherit content type and object ID from the parent root comment
            data['content_type'] = parent.content_type
            data['target_id'] = parent.object_id

        return data

    def create(self, validated_data):
        # target_type and target_id are write_only fields and not part of the model.
        # We need to pop them so we don't pass them to Comment.objects.create()
        validated_data.pop('target_type', None)
        validated_data.pop('target_id', None)
        
        comment = super().create(validated_data)
        
        # Parse and set mentions
        users = parse_mentions(comment.body)
        comment.mentions.set(users)
        return comment

    def update(self, instance, validated_data):
        validated_data.pop('target_type', None)
        validated_data.pop('target_id', None)
        
        instance = super().update(instance, validated_data)
        users = parse_mentions(instance.body)
        instance.mentions.set(users)
        return instance