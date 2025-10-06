from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from datetime import datetime

class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.5
    changefreq = 'weekly'
    
    def items(self):
        return ['home', 'rooms', 'gallery', 'contact']
    
    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        # Return the last modification date for each page
        # You can customize this based on when each page was last updated
        return datetime(2024, 12, 19)

class HomePageSitemap(Sitemap):
    """Sitemap for the homepage with highest priority"""
    priority = 1.0
    changefreq = 'weekly'
    
    def items(self):
        return ['home']
    
    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        return datetime(2024, 12, 19)

class RoomsPageSitemap(Sitemap):
    """Sitemap for the rooms page"""
    priority = 0.9
    changefreq = 'monthly'
    
    def items(self):
        return ['rooms']
    
    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        return datetime(2024, 12, 19)

class GalleryPageSitemap(Sitemap):
    """Sitemap for the gallery page"""
    priority = 0.8
    changefreq = 'monthly'
    
    def items(self):
        return ['gallery']
    
    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        return datetime(2024, 12, 19)

class ContactPageSitemap(Sitemap):
    """Sitemap for the contact page"""
    priority = 0.7
    changefreq = 'monthly'
    
    def items(self):
        return ['contact']
    
    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        return datetime(2024, 12, 19)
