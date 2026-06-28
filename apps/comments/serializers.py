from rest_framework import serializers
from apps.users.serializers import UserDetailSerializer
from .models import Comment
from .mention_parser import parse_mentions

class ReplySerializer(serializers.ModelSerializer):
    author = UserDetailSerializer(read_only=True)
    mentions = UserDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'body', 'mentions', 'parent', 'created_at', 'updated_at']
        read_only_fields = ['id', 'task', 'author', 'mentions', 'created_at', 'updated_at']

class CommentSerializer(serializers.ModelSerializer):
    author = UserDetailSerializer(read_only=True)
    mentions = UserDetailSerializer(many=True, read_only=True)
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'body', 'mentions', 'parent', 'replies', 'created_at', 'updated_at']
        read_only_fields = ['id', 'task', 'author', 'mentions', 'created_at', 'updated_at']

    def validate_body(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("Comment body cannot be empty.")
        if len(value) > 5000:
            raise serializers.ValidationError("Comment body cannot exceed 5000 characters.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        if request:
            validated_data['author'] = request.user
        comment = super().create(validated_data)
        users = parse_mentions(comment.body)
        comment.mentions.set(users)
        return comment

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        users = parse_mentions(instance.body)
        instance.mentions.set(users)
        return instance
