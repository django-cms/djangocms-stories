###########
Permissions
###########

djangocms-stories integrates with Django's permission system and Django CMS's advanced permission framework.

Permission Model
================

**Django Model Permissions**
  Standard Django permissions apply:
  - ``add_post`` - Create new stories
  - ``change_post`` - Edit existing stories
  - ``delete_post`` - Delete stories
  - ``view_post`` - View stories (Django 2.1+)

**Category Permissions**
  - ``add_postcategory`` - Create categories
  - ``change_postcategory`` - Edit categories
  - ``delete_postcategory`` - Delete categories

**Configuration Permissions**
  - ``add_storiesconfig`` - Create app configurations
  - ``change_storiesconfig`` - Modify configurations
  - ``delete_storiesconfig`` - Remove configurations

Django CMS Integration
======================

**Page Permissions**
  Stories inherit permissions from their attached page:
  - Page view restrictions apply to stories
  - Edit permissions control story management
  - Publish permissions affect story visibility

**Toolbar Integration**
  - Toolbar items respect permissions
  - Context-sensitive menu options
  - Role-based interface customization

**Placeholder Permissions**
  - Plugin editing permissions
  - Structure vs content editing
  - Language-specific permissions

User Roles and Workflows
=========================

**Content Creators**
  Typical permissions:
  - Add and edit own stories
  - View all published stories
  - Use basic plugins

**Editors**
  Extended permissions:
  - Edit all stories
  - Manage categories and tags
  - Access advanced plugins
  - Preview unpublished content

**Publishers**
  Publication control:
  - Publish/unpublish stories
  - Schedule publication dates
  - Manage featured content

**Administrators**
  Full access:
  - Manage configurations
  - User permission management
  - System settings control

Custom Permission Logic
=======================

**Author-Based Permissions**
  Restrict editing to authors::

    class PostAdmin(admin.ModelAdmin):
        def get_queryset(self, request):
            qs = super().get_queryset(request)
            if not request.user.is_superuser:
                qs = qs.filter(author=request.user)
            return qs

**Group-Based Access**
  Organize users by publication groups::

    class StoryPermissionMixin:
        def has_change_permission(self, request, obj=None):
            if obj and obj.author != request.user:
                # Check if user is in same editorial group
                return request.user.groups.filter(
                    name=f"editors_{obj.app_config.namespace}"
                ).exists()
            return super().has_change_permission(request, obj)

Configuration-Level Permissions
===============================

**Namespace Isolation**
  Separate permissions per configuration::

    # Custom manager for permission filtering
    class ConfigPermissionManager(models.Manager):
        def for_user(self, user):
            if user.is_superuser:
                return self.all()

            # Filter by user's allowed configurations
            allowed_configs = user.groups.values_list(
                'storiesconfig__pk', flat=True
            )
            return self.filter(app_config__pk__in=allowed_configs)

**Multi-Site Permissions**
  Site-specific access control::

    class SitePermissionMixin:
        def get_queryset(self, request):
            qs = super().get_queryset(request)
            if not request.user.is_superuser:
                current_site = get_current_site(request)
                qs = qs.filter(app_config__site=current_site)
            return qs

API and Frontend Permissions
=============================

**View-Level Permissions**
  Control access to story views::

    class PostDetailView(DetailView):
        def dispatch(self, request, *args, **kwargs):
            post = self.get_object()
            if not post.is_published and not request.user.has_perm('stories.change_post'):
                raise PermissionDenied
            return super().dispatch(request, *args, **kwargs)

**Template Permissions**
  Show/hide elements based on permissions::

    {% if perms.djangocms_stories.add_post %}
        <a href="{% url 'admin:djangocms_stories_post_add' %}">
            Add New Story
        </a>
    {% endif %}

**API Permissions**
  REST API permission classes::

    from rest_framework.permissions import BasePermission

    class IsAuthorOrReadOnly(BasePermission):
        def has_object_permission(self, request, view, obj):
            if request.method in ['GET', 'HEAD', 'OPTIONS']:
                return True
            return obj.author == request.user

Advanced Permission Scenarios
==============================

**Workflow Permissions**
  Multi-stage approval process::

    class WorkflowPermission:
        DRAFT = 'draft'
        REVIEW = 'review'
        APPROVED = 'approved'
        PUBLISHED = 'published'

        @classmethod
        def can_transition(cls, user, from_status, to_status):
            transitions = {
                (cls.DRAFT, cls.REVIEW): 'stories.submit_for_review',
                (cls.REVIEW, cls.APPROVED): 'stories.approve_post',
                (cls.APPROVED, cls.PUBLISHED): 'stories.publish_post',
            }
            required_perm = transitions.get((from_status, to_status))
            return user.has_perm(required_perm) if required_perm else False

**Time-Based Permissions**
  Temporary access control::

    class TemporaryPermission(models.Model):
        user = models.ForeignKey(User, on_delete=models.CASCADE)
        post = models.ForeignKey(Post, on_delete=models.CASCADE)
        permission_type = models.CharField(max_length=50)
        expires_at = models.DateTimeField()

        @classmethod
        def user_has_temp_permission(cls, user, post, perm_type):
            return cls.objects.filter(
                user=user,
                post=post,
                permission_type=perm_type,
                expires_at__gt=timezone.now()
            ).exists()

Permission Testing
==================

**Unit Tests**
  Test permission logic::

    class PermissionTestCase(TestCase):
        def test_author_can_edit_own_post(self):
            user = User.objects.create_user('author')
            post = Post.objects.create(author=user)

            self.assertTrue(
                post.author == user and
                user.has_perm('stories.change_post')
            )

**Integration Tests**
  Test view-level permissions::

    def test_unauthorized_edit_redirects(self):
        response = self.client.get('/stories/edit/1/')
        self.assertRedirects(response, '/login/')

**Permission Auditing**
  Log permission checks::

    import logging

    class PermissionAuditMixin:
        def has_permission(self, request, view):
            result = super().has_permission(request, view)
            logging.info(f"Permission check: {request.user} -> {view} = {result}")
            return result

Best Practices
==============

**Principle of Least Privilege**
  - Grant minimum necessary permissions
  - Regular permission audits
  - Remove unused permissions

**Role-Based Access Control**
  - Define clear user roles
  - Group-based permission assignment
  - Consistent permission patterns

**Permission Documentation**
  - Document custom permissions
  - Maintain permission matrices
  - User training on permission model
