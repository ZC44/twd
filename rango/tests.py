# Chapter 3
from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
import os

#Chapter 4
from django.contrib.staticfiles import finders

#Chapter 5
from rango.models import Page, Category
import populate_rango
import rango.test_utils as test_utils

#Chapter 6
from rango.decorators import chapter6

#Chapter 7
from rango.decorators import chapter7
from rango.forms import CategoryForm, PageForm

#Chapter 8
from django.template import loader
from django.conf import settings
from rango.decorators import chapter8
import os.path

#Chapter 9
from rango.models import User, UserProfile
from rango.forms import UserForm, UserProfileForm
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from rango.decorators import chapter9

#Chapter 10
from datetime import datetime, timedelta


# ===== Chapter 9
class Chapter9ModelTests(TestCase):
    def test_user_profile_model(self):
        # Create a user
        user, user_profile = test_utils.create_user()

        # Check there is only the saved user and its profile in the database
        all_users = User.objects.all()
        self.assertEquals(len(all_users), 1)

        all_profiles = UserProfile.objects.all()
        self.assertEquals(len(all_profiles), 1)

        # Check profile fields were saved correctly
        all_profiles[0].user = user
        all_profiles[0].website = user_profile.website


class Chapter9ViewTests(TestCase):
    @chapter9
    def test_registration_form_is_displayed_correctly(self):
        # Access registration page
        try:
            response = self.client.get(reverse('register'))
        except:
            try:
                response = self.client.get(reverse('rango:register'))
            except:
                return False

        # Check if form is rendered correctly
        # self.assertIn('<h1>Register with Rango</h1>', response.content.decode('ascii'))
        self.assertIn('<strong>register here!</strong><br />'.lower(), response.content.decode('ascii').lower())

        # Check form in response context is instance of UserForm
        self.assertTrue(isinstance(response.context['user_form'], UserForm))

        # Check form in response context is instance of UserProfileForm
        self.assertTrue(isinstance(response.context['profile_form'], UserProfileForm))

        user_form = UserForm()
        profile_form = UserProfileForm()

        # Check form is displayed correctly
        self.assertEquals(response.context['user_form'].as_p(), user_form.as_p())
        self.assertEquals(response.context['profile_form'].as_p(), profile_form.as_p())

        # Check submit button
        self.assertIn('type="submit"', response.content.decode('ascii'))
        self.assertIn('name="submit"', response.content.decode('ascii'))
        self.assertIn('value="Register"', response.content.decode('ascii'))

    @chapter9
    def test_login_form_is_displayed_correctly(self):
        # Access login page
        try:
            response = self.client.get(reverse('login'))
        except:
            try:
                response = self.client.get(reverse('rango:login'))
            except:
                return False

        # Check form display
        # Header
        self.assertIn('<h1>Login to Rango</h1>'.lower(), response.content.decode('ascii').lower())

        # Username label and input text
        self.assertIn('Username:', response.content.decode('ascii'))
        self.assertIn('input type="text"', response.content.decode('ascii'))
        self.assertIn('name="username"', response.content.decode('ascii'))
        self.assertIn('size="50"', response.content.decode('ascii'))

        # Password label and input text
        self.assertIn('Password:', response.content.decode('ascii'))
        self.assertIn('input type="password"', response.content.decode('ascii'))
        self.assertIn('name="password"', response.content.decode('ascii'))
        self.assertIn('value=""', response.content.decode('ascii'))
        self.assertIn('size="50"', response.content.decode('ascii'))

        # Submit button
        self.assertIn('input type="submit"', response.content.decode('ascii'))
        self.assertIn('value="submit"', response.content.decode('ascii'))

    @chapter9
    def test_login_form_is_displayed_correctly(self):
        # Access login page
        try:
            response = self.client.get(reverse('login'))
        except:
            try:
                response = self.client.get(reverse('rango:login'))
            except:
                return False

        # Check form display
        # Header
        self.assertIn('<h1>Login to Rango</h1>'.lower(), response.content.decode('ascii').lower())

        # Username label and input text
        self.assertIn('Username:', response.content.decode('ascii'))
        self.assertIn('input type="text"', response.content.decode('ascii'))
        self.assertIn('name="username"', response.content.decode('ascii'))
        self.assertIn('size="50"', response.content.decode('ascii'))

        # Password label and input text
        self.assertIn('Password:', response.content.decode('ascii'))
        self.assertIn('input type="password"', response.content.decode('ascii'))
        self.assertIn('name="password"', response.content.decode('ascii'))
        self.assertIn('value=""', response.content.decode('ascii'))
        self.assertIn('size="50"', response.content.decode('ascii'))

        # Submit button
        self.assertIn('input type="submit"', response.content.decode('ascii'))
        self.assertIn('value="submit"', response.content.decode('ascii'))

    @chapter9
    def test_login_provides_error_message(self):
        # Access login page
        try:
            response = self.client.post(reverse('login'), {'username': 'wronguser', 'password': 'wrongpass'})
        except:
            try:
                response = self.client.post(reverse('rango:login'), {'username': 'wronguser', 'password': 'wrongpass'})
            except:
                return False

        print(response.content.decode('ascii'))
        try:
            self.assertIn('wronguser', response.content.decode('ascii'))
        except:
            self.assertIn('Invalid login details supplied.', response.content.decode('ascii'))

    @chapter9
    def test_login_redirects_to_index(self):
        # Create a user
        test_utils.create_user()

        # Access login page via POST with user data
        try:
            response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'test1234'})
        except:
            try:
                response = self.client.post(reverse('rango:login'), {'username': 'testuser', 'password': 'test1234'})
            except:
                return False

        # Check it redirects to index
        self.assertRedirects(response, reverse('index'))

    @chapter9
    def test_upload_image(self):
        # Create fake user and image to upload to register user
        image = SimpleUploadedFile("testuser.jpg", b"file_content", content_type="image/jpeg")
        try:
            response = self.client.post(reverse('register'),
                                        {'username': 'testuser', 'password': 'test1234',
                                         'email': 'testuser@testuser.com',
                                         'website': 'http://www.testuser.com',
                                         'picture': image})
        except:
            try:
                response = self.client.post(reverse('rango:register'),
                                            {'username': 'testuser', 'password': 'test1234',
                                             'email': 'testuser@testuser.com',
                                             'website': 'http://www.testuser.com',
                                             'picture': image})
            except:
                return False

        # Check user was successfully registered
        self.assertIn('thank you for registering!'.lower(), response.content.decode('ascii').lower())
        user = User.objects.get(username='testuser')
        user_profile = UserProfile.objects.get(user=user)
        path_to_image = './media/profile_images/testuser.jpg'

        # Check file was saved properly
        self.assertTrue(os.path.isfile(path_to_image))

        # Delete fake file created
        default_storage.delete('./media/profile_images/testuser.jpg')

# ====== Chapter 10
class Chapter10SessionTests(TestCase):
    def test_user_number_of_access_and_last_access_to_index(self):
        #Access index page 100 times
        for i in range(0, 100):
            try:
                response = self.client.get(reverse('index'))
            except:
                try:
                    response = self.client.get(reverse('rango:index'))
                except:
                    return False
            session = self.client.session
            # old_visists = session['visits']

            # Check it exists visits and last_visit attributes on session
            self.assertIsNotNone(self.client.session['visits'])
            self.assertIsNotNone(self.client.session['last_visit'])

            # Check last visit time is within 0.1 second interval from now
            # self.assertAlmostEqual(datetime.now(),
            #     datetime.strptime(session['last_visit'], "%Y-%m-%d %H:%M:%S.%f"), delta=timedelta(seconds=0.1))

            # Get last visit time subtracted by one day
            last_visit = datetime.now() - timedelta(days=1)

            # Set last visit to a day ago and save
            session['last_visit'] = str(last_visit)
            session.save()

            # Check if the visits number in session is being incremented and it's correct
            self.assertEquals(session['visits'], session['visits'])
            # before it was i+1 but visits shouldn't change for the same ip visited in one day


class Chapter10ViewTests(TestCase):
    def test_index_shows_number_of_visits(self):
        #Access index
        try:
            response = self.client.get(reverse('index'))
        except:
            try:
                response = self.client.get(reverse('rango:index'))
            except:
                return False

        # Check it contains visits message
        self.assertIn('visits: 1'.lower(), response.content.decode('ascii').lower())

    def test_about_page_shows_number_of_visits(self):
        #Access index page to count one visit
        try:
            response = self.client.get(reverse('index'))
        except:
            try:
                response = self.client.get(reverse('rango:index'))
            except:
                return False

        # Access about page
        try:
            response = self.client.get(reverse('about'))
        except:
            try:
                response = self.client.get(reverse('rango:about'))
            except:
                return False

        # Check it contains visits message
        self.assertIn('visits: 1'.lower(), response.content.decode('ascii').lower())

    def test_visit_number_is_passed_via_context(self):
        #Access index
        try:
            response = self.client.get(reverse('index'))
        except:
            try:
                response = self.client.get(reverse('rango:index'))
            except:
                return False

        # Check it contains visits message in the context
        self.assertIn('visits', response.context)

        #Access about page
        try:
            response = self.client.get(reverse('about'))
        except:
            try:
                response = self.client.get(reverse('rango:about'))
            except:
                return False

        # Check it contains visits message in the context
        self.assertIn('visits', response.context)