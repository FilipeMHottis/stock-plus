from django.db import models
import os
from django.core.files.base import ContentFile
from .tag import Tag
from .category import Category
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q


class Product(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to='products/',
        default='products/product_default.png',
    )
    description = models.TextField()
    stock = models.IntegerField(default=0)
    barcode = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='products',
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def upload_image(self, image_file):
        """Salva uma nova imagem para o produto com nome padronizado."""
        ext = os.path.splitext(image_file.name)[1]
        filename = f"product_{self.id}{ext}"
        self.image.save(filename, ContentFile(image_file.read()), save=True)

    def add_tag(self, tag):
        '''Adiciona uma tag ao produto.'''
        self.tags.add(tag)

    def remove_tag(self, tag):
        '''Remove uma tag do produto.'''
        self.tags.remove(tag)

    @staticmethod
    def search_products(query: str):
        """
        Realiza uma busca inteligente por produtos:
        - Procura correspondência parcial (icontains)
        - Usa similaridade de texto (TrigramSimilarity)
        - Busca em: nome, descrição, categoria e tags
        - Ordena por relevância
        """

        if not query.strip():
            return Product.objects.none()

        # Busca com trigramas (fuzzy search)
        products = (
            Product.objects
            .annotate(
                similarity=(
                    TrigramSimilarity('name', query) +
                    TrigramSimilarity('description', query) +
                    TrigramSimilarity('category__name', query)
                )
            )
            .filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(barcode__icontains=query) |
                Q(category__name__icontains=query) |
                Q(tags__name__icontains=query) |
                Q(similarity__gt=0.2)  # tolerância de similaridade
            )
            .distinct()
            .order_by('-similarity')  # mais parecidos primeiro
        )

        return products

    class Meta:
        ordering = ['name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
