from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.dispatch import receiver
from django.db.models.signals import post_save
# from PIL import Image
from django_resized import ResizedImageField
from account.countries import countries
import geocoder


class MyAccountManager(BaseUserManager):
	def create_user(self, email, username, password=None):
		if not email:
			raise ValueError('Users must have an email address')
		if not username:
			raise ValueError('Users must have a username')

		user = self.model(
			email=self.normalize_email(email),
			username=username,
		)

		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, username, password):
		user = self.create_user(
			email=self.normalize_email(email),
			password=password,
			username=username,
		)
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)
		return user
	
	


class UserAccount(AbstractBaseUser):
	location 				= models.CharField(max_length=500, blank=True, null=True)
	latitude 				= models.FloatField(default=0)
	longitude 				= models.FloatField(default=0)
	bio 					= models.TextField(blank=True, null=True)
	email 					= models.EmailField(verbose_name="email", max_length=60, unique=True)
	username 				= models.CharField(max_length=30, unique=True)
	first_name          	= models.CharField(max_length=30, unique=False)
	last_name 				= models.CharField(max_length=30, unique=False)
	phone   				= models.CharField(max_length=30, unique=False)
	date_joined				= models.DateTimeField(verbose_name='date joined', auto_now_add=True)
	last_login				= models.DateTimeField(verbose_name='last login', auto_now=True)
	is_admin				= models.BooleanField(default=False)
	is_active				= models.BooleanField(default=True)
	is_staff				= models.BooleanField(default=True)
	is_subscribed				= models.BooleanField(default=False)
	is_superuser			= models.BooleanField(default=False)


	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username']

	objects = MyAccountManager()

	def __str__(self):
		return self.email 	# For checking permissions. to keep it simple all admin have ALL permissons

	def has_perm(self, perm, obj=None):
		return self.is_admin 	# Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)

	def has_module_perms(self, app_label):
		return True

	
	class Meta:
		verbose_name = "User"
		verbose_name_plural = "Users"

	def usern(self):
		return self.username

	def save(self, *args, **kwargs):
		# self.latitude = geocoder.osm(self.country).lat
		# self.longitude = geocoder.osm(self.country).lng
		return super().save(*args, **kwargs)



class Profile(models.Model):
	user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
	image = ResizedImageField(size=[300, 300], crop=['middle', 'center'], default="profile_pics/default.png", upload_to="profile_pics")


	def __str__(self):
		return f"{self.user.username}'s Profile"


	@receiver(post_save, sender=UserAccount)
	def create_profile(sender, instance, created, **kwargs):
		if created:
			Profile.objects.create(user=instance)
			

	@receiver(post_save, sender=UserAccount)
	def save_profile(sender, instance, **kwargs):
		instance.profile.save()

	class Meta:
		verbose_name = "Profile"
		verbose_name_plural = "Profiles"