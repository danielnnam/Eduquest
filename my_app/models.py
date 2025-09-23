from django.db import models
from django.utils.text import slugify

# Create your models here.

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)  # for SEO-friendly URLs
    author = models.CharField(max_length=100, default="Admin")
    content = models.TextField()
    excerpt = models.TextField(max_length=300, blank=True, help_text="Short summary for preview")
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.excerpt:
            self.excerpt = self.content[:200]  # auto-generate if not provided
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
