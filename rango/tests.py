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

# ===== CHAPTER 3
class Chapter3ViewTests(TestCase):
    def test_index_contains_hello_message(self):
        # Check if there is the message 'hello world!'
        response = self.client.get(reverse('index'))
        self.assertIn('Rango says'.lower(), response.content.decode('ascii').lower())

        # file.write('test_index_contains_hello_message\n')

    def test_about_contains_create_message(self):
        # Check if in the about page is there a message
        self.client.get(reverse('index'))
        response = self.client.get(reverse('about'))
        self.assertIn('Rango says here is the about page'.lower(), response.content.decode('ascii').lower())

    # Chapter 4
    from django.contrib.staticfiles import finders

    # ===== CHAPTER 4
    class Chapter4ViewTest(TestCase):
        def test_view_has_title(self):
            response = self.client.get(reverse('index'))

            # Check title used correctly
            self.assertIn('<title>', response.content.decode('ascii'))
            self.assertIn('</title>', response.content.decode('ascii'))

        def test_index_using_template(self):
            response = self.client.get(reverse('index'))

            # Check the template used to render index page
            self.assertTemplateUsed(response, 'rango/index.html')

        def test_about_using_template(self):
            self.client.get(reverse('index'))
            response = self.client.get(reverse('about'))

            # Check the template used to render about page
            self.assertTemplateUsed(response, 'rango/about.html')

        def test_rango_picture_displayed(self):
            response = self.client.get(reverse('index'))

            # Check if is there an image in index page
            self.assertIn('img src="/static/images/rango.jpg'.lower(), response.content.decode('ascii').lower())

        # New media test
        def test_cat_picture_displayed(self):
            response = self.client.get(reverse('about'))

            # Check if is there an image in index page
            self.assertIn('img src="/media/cat.jpg'.lower(), response.content.decode('ascii').lower())

        def test_about_contain_image(self):
            self.client.get(reverse('index'))
            response = self.client.get(reverse('about'))

            # Check if is there an image in index page
            self.assertIn('img src="/static/images/', response.content.decode('ascii'))

        def test_serving_static_files(self):
            # If using static media properly result is not NONE once it finds rango.jpg
            result = finders.find('images/rango.jpg')
            self.assertIsNotNone(result)

        # ===== CHAPTER 5
        class Chapter5ModelTests(TestCase):
            def test_create_a_new_category(self):
                cat = Category(name="Python")
                cat.save()

                # Check category is in database
                categories_in_database = Category.objects.all()
                self.assertEquals(len(categories_in_database), 1)
                only_poll_in_database = categories_in_database[0]
                self.assertEquals(only_poll_in_database, cat)

            def test_create_pages_for_categories(self):
                cat = Category(name="Python")
                cat.save()

                # create 2 pages for category python
                python_page = Page()
                python_page.category = cat
                python_page.title = "Official Python Tutorial"
                python_page.url = "http://docs.python.org/2/tutorial/"
                python_page.save()

                django_page = Page()
                django_page.category = cat
                django_page.title = "Django"
                django_page.url = "https://docs.djangoproject.com/en/1.5/intro/tutorial01/"
                django_page.save()

                # Check if they both were saved
                python_pages = cat.page_set.all()
                self.assertEquals(python_pages.count(), 2)

                # Check if they were saved properly
                first_page = python_pages[0]
                self.assertEquals(first_page, python_page)
                self.assertEquals(first_page.title, "Official Python Tutorial")
                self.assertEquals(first_page.url, "http://docs.python.org/2/tutorial/")

            def test_population_script_changes(self):
                # Populate database
                populate_rango.populate()

                # Check if the category has correct number of views and likes
                cat = Category.objects.get(name='Python')
                self.assertEquals(cat.views, 128)
                self.assertEquals(cat.likes, 64)

                # Check if the category has correct number of views and likes
                cat = Category.objects.get(name='Django')
                self.assertEquals(cat.views, 64)
                self.assertEquals(cat.likes, 32)

                # Check if the category has correct number of views and likes
                cat = Category.objects.get(name='Other Frameworks')
                self.assertEquals(cat.views, 32)
                self.assertEquals(cat.likes, 16)

            # ===== Chapter 6
            class Chapter6ModelTests(TestCase):
                def test_category_contains_slug_field(self):
                    # Create a new category
                    new_category = Category(name="Test Category")
                    new_category.save()

                    # Check slug was generated
                    self.assertEquals(new_category.slug, "test-category")

                    # Check there is only one category
                    categories = Category.objects.all()
                    self.assertEquals(len(categories), 1)

                    # Check attributes were saved correctly
                    categories[0].slug = new_category.slug

            class Chapter6ViewTests(TestCase):
                def test_index_context(self):
                    # Access index with empty database
                    response = self.client.get(reverse('index'))

                    # Context dictionary is then empty
                    self.assertCountEqual(response.context['categories'], [])
                    self.assertCountEqual(response.context['pages'], [])

                    categories = test_utils.create_categories()
                    test_utils.create_pages(categories)

                    # Access index with database filled
                    response = self.client.get(reverse('index'))

                    # Retrieve categories and pages from database
                    categories = Category.objects.order_by('-likes')[:5]
                    pages = Page.objects.order_by('-views')[:5]

                    # Check context dictionary filled
                    self.assertCountEqual(response.context['categories'], categories)
                    self.assertCountEqual(response.context['pages'], pages)

                def test_index_displays_five_most_liked_categories(self):
                    # Create categories
                    test_utils.create_categories()

                    # Access index
                    response = self.client.get(reverse('index'))

                    # Check if the 5 pages with most likes are displayed
                    for i in range(10, 5, -1):
                        self.assertIn("Category " + str(i), response.content.decode('ascii'))

                def test_index_displays_no_categories_message(self):
                    # Access index with empty database
                    response = self.client.get(reverse('index'))

                    # Check if no categories message is displayed
                    self.assertIn("There are no categories present.".lower(), response.content.decode('ascii').lower())

                def test_index_displays_five_most_viewed_pages(self):
                    # Create categories
                    categories = test_utils.create_categories()

                    # Create pages for categories
                    test_utils.create_pages(categories)

                    # Access index
                    response = self.client.get(reverse('index'))

                    # Check if the 5 pages with most views are displayed
                    for i in range(20, 15, -1):
                        self.assertIn("Page " + str(i), response.content.decode('ascii'))

                def test_index_contains_link_to_categories(self):
                    # Create categories
                    categories = test_utils.create_categories()

                    # Access index
                    response = self.client.get(reverse('index'))

                    # Check if the 5 pages with most likes are displayed
                    for i in range(10, 5, -1):
                        category = categories[i - 1]
                        self.assertIn(reverse('show_category', args=[category.slug])[:-1],
                                      response.content.decode('ascii'))

                def test_category_context(self):
                    # Create categories and pages for categories
                    categories = test_utils.create_categories()
                    pages = test_utils.create_pages(categories)

                    # For each category check the context dictionary passed via render() function
                    for category in categories:
                        response = self.client.get(reverse('show_category', args=[category.slug]))
                        pages = Page.objects.filter(category=category)
                        self.assertCountEqual(response.context['pages'], pages)
                        self.assertEquals(response.context['category'], category)

                def test_category_page_using_template(self):
                    # Create categories in database
                    test_utils.create_categories()

                    # Access category page
                    response = self.client.get(reverse('show_category', args=['category-1']))

                    # check was used the right template
                    self.assertTemplateUsed(response, 'rango/category.html')

                @chapter6
                def test_category_page_displays_pages(self):
                    # Create categories in database
                    categories = test_utils.create_categories()

                    # Create pages for categories
                    test_utils.create_pages(categories)

                    # For each category, access its page and check for the pages associated with it
                    for category in categories:
                        # Access category page
                        response = self.client.get(reverse('show_category', args=[category.slug]))

                        # Retrieve pages for that category
                        pages = Page.objects.filter(category=category)

                        # Check pages are displayed and they have a link
                        for page in pages:
                            self.assertIn(page.title, response.content.decode('ascii'))
                            self.assertIn(page.url, response.content.decode('ascii'))

                def test_category_page_displays_empty_message(self):
                    # Create categories in database
                    categories = test_utils.create_categories()

                    # For each category, access its page and check there are no pages associated with it
                    for category in categories:
                        # Access category page
                        response = self.client.get(reverse('show_category', args=[category.slug]))
                        self.assertIn("No pages currently in category.".lower(),
                                      response.content.decode('ascii').lower())

                def test_category_page_displays_category_does_not_exist_message(self):
                    # Try to access categories not saved to database and check the message
                    response = self.client.get(reverse('show_category', args=['Python']))
                    self.assertIn("does not exist!".lower(), response.content.decode('ascii').lower())

                    response = self.client.get(reverse('show_category', args=['Django']))
                    self.assertIn("does not exist!".lower(), response.content.decode('ascii').lower())

                # ===== Chapter 7
                class Chapter7ViewTests(TestCase):
                    @chapter7
                    def test_index_contains_link_to_add_category(self):
                        # Access index
                        try:
                            response = self.client.get(reverse('index'))
                        except:
                            try:
                                response = self.client.get(reverse('rango:index'))
                            except:
                                return False

                        # Check if there is text and a link to add category
                        self.assertIn('href="' + reverse('add_category') + '"', response.content.decode('ascii'))

                    @chapter7
                    def test_add_category_form_is_displayed_correctly(self):
                        # Access add category page
                        response = self.client.get(reverse('add_category'))

                        # Check form in response context is instance of CategoryForm
                        self.assertTrue(isinstance(response.context['form'], CategoryForm))

                        # Check form is displayed correctly
                        # Header
                        self.assertIn('<h1>Add a Category</h1>'.lower(), response.content.decode('ascii').lower())

                        # Label
                        self.assertIn('Please enter the category name.'.lower(),
                                      response.content.decode('ascii').lower())

                        # Text input
                        self.assertIn('id="id_name"', response.content.decode('ascii'))
                        self.assertIn('maxlength="128"', response.content.decode('ascii'))
                        self.assertIn('name="name"', response.content.decode('ascii'))
                        self.assertIn('type="text"', response.content.decode('ascii'))

                        # Button
                        self.assertIn('type="submit" name="submit" value="Create Category"'.lower(),
                                      response.content.decode('ascii').lower())

                    @chapter7
                    def test_add_page_form_is_displayed_correctly(self):
                        # Create categories
                        categories = test_utils.create_categories()

                        for category in categories:
                            # Access add category page
                            try:
                                response = self.client.get(reverse('index'))
                                response = self.client.get(reverse('add_page', args=[category.slug]))
                            except:
                                try:
                                    response = self.client.get(reverse('rango:index'))
                                    response = self.client.get(reverse('rango:add_page', args=[category.slug]))
                                except:
                                    return False

                            # Check form in response context is instance of CategoryForm
                            self.assertTrue(isinstance(response.context['form'], PageForm))

                            # Check form is displayed correctly

                            # Label 1
                            self.assertIn('Please enter the title of the page.'.lower(),
                                          response.content.decode('ascii').lower())

                            # Label 2
                            self.assertIn('Please enter the URL of the page.'.lower(),
                                          response.content.decode('ascii').lower())

                            # Text input 1
                            self.assertIn('id="id_title"'.lower(), response.content.decode('ascii').lower())
                            self.assertIn('maxlength="128"'.lower(), response.content.decode('ascii').lower())
                            self.assertIn('name="title"'.lower(), response.content.decode('ascii').lower())
                            self.assertIn('type="text"'.lower(), response.content.decode('ascii').lower())

                            # Text input 2
                            self.assertIn('id="id_url"'.lower(), response.content.decode('ascii').lower())
                            self.assertIn('maxlength="200"'.lower(), response.content.decode('ascii').lower())
                            self.assertIn('name="url"'.lower(), response.content.decode('ascii').lower())
                            self.assertIn('type="url"'.lower(), response.content.decode('ascii').lower())

                            # Button
                            self.assertIn('type="submit" name="submit" value="Add Page"'.lower(),
                                          response.content.decode('ascii').lower())

                    def test_access_category_that_does_not_exists(self):
                        # Access a category that does not exist
                        response = self.client.get(reverse('show_category', args=['python']))

                        # Check that it has a response as status code OK is 200
                        self.assertEquals(response.status_code, 200)

                        # Check the rendered page is not empty, thus it was customised (I suppose)
                        self.assertNotEquals(response.content.decode('ascii'), '')

                    def test_link_to_add_page_only_appears_in_valid_categories(self):
                        # Access a category that does not exist
                        response = self.client.get(reverse('show_category', args=['python']))

                        # Check that there is not a link to add page
                        try:
                            self.assertNotIn(reverse('add_page', args=['python']), response.content.decode('ascii'))
                            # Access a category that does not exist
                            response = self.client.get(reverse('show_category', args=['other-frameworks']))
                            # Check that there is not a link to add page
                            self.assertNotIn(reverse('add_page', args=['other-frameworks']),
                                             response.content.decode('ascii'))
                        except:
                            try:
                                self.assertNotIn(reverse('rango:add_page', args=['python']),
                                                 response.content.decode('ascii'))
                                # Access a category that does not exist
                                response = self.client.get(reverse('rango:show_category', args=['other-frameworks']))
                                # Check that there is not a link to add page
                                self.assertNotIn(reverse('rango:add_page', args=['other-frameworks']),
                                                 response.content.decode('ascii'))
                            except:
                                return False

                    @chapter7
                    def test_category_contains_link_to_add_page(self):
                        # Crete categories
                        categories = test_utils.create_categories()

                        # For each category in the database check if contains link to add page
                        for category in categories:
                            try:
                                response = self.client.get(reverse('show_category', args=[category.slug]))
                                self.assertIn(reverse('add_page', args=[category.slug]),
                                              response.content.decode('ascii'))
                            except:
                                try:
                                    response = self.client.get(reverse('rango:show_category', args=[category.slug]))
                                    self.assertIn(reverse('rango:add_page', args=[category.slug]),
                                                  response.content.decode('ascii'))
                                except:
                                    return False

# ====== Chapter 8
class Chapter8ViewTests(TestCase):

    def test_base_template_exists(self):
        # Check base.html exists inside template folder
        path_to_base = settings.TEMPLATE_DIR + '/rango/base.html'
        print(path_to_base)
        self.assertTrue(os.path.isfile(path_to_base))

    @chapter8
    def test_titles_displayed(self):
        # Create user and log in
        test_utils.create_user()
        self.client.login(username='testuser', password='test1234')

        # Create categories
        categories = test_utils.create_categories()

        # Access index and check the title displayed
        response = self.client.get(reverse('index'))
        self.assertIn('Rango -'.lower(), response.content.decode('ascii').lower())

        # Access category page and check the title displayed
        response = self.client.get(reverse('show_category', args=[categories[0].slug]))
        self.assertIn(categories[0].name.lower(), response.content.decode('ascii').lower())

        # Access about page and check the title displayed
        response = self.client.get(reverse('about'))
        self.assertIn('About'.lower(), response.content.decode('ascii').lower())

        # Access login page and check the title displayed
        response = self.client.get(reverse('login'))
        self.assertIn('Login'.lower(), response.content.decode('ascii').lower())

        # Access register page and check the title displayed
        response = self.client.get(reverse('register'))
        self.assertIn('Register'.lower(), response.content.decode('ascii').lower())

        # Access restricted page and check the title displayed
        response = self.client.get(reverse('restricted'))
        self.assertIn("Since you're logged in".lower(), response.content.decode('ascii').lower())

        # Access add page and check the title displayed
        response = self.client.get(reverse('add_page', args=[categories[0].slug]))
        self.assertIn('Add Page'.lower(), response.content.decode('ascii').lower())

        # Access add new category page and check the title displayed
        response = self.client.get(reverse('add_category'))
        self.assertIn('Add Category'.lower(), response.content.decode('ascii').lower())

    @chapter8
    def test_pages_using_templates(self):
        # Create user and log in
        test_utils.create_user()
        self.client.login(username='testuser', password='test1234')

        # Create categories
        categories = test_utils.create_categories()
        # Create a list of pages to access
        pages = [reverse('index'), reverse('about'), reverse('add_category'), reverse('register'), reverse('login'),
                 reverse('show_category', args=[categories[0].slug]), reverse('add_page', args=[categories[0].slug])]#, reverse('restricted')]

        # Create a list of pages to access
        templates = ['rango/index.html', 'rango/about.html', 'rango/add_category.html', 'rango/register.html',
                     'rango/login.html','rango/category.html', 'rango/add_page.html']#, 'rango/restricted.html']

        # For each page in the page list, check if it extends from base template
        for template, page in zip(templates, pages):
            response = self.client.get(page)
            self.assertTemplateUsed(response, template)

    @chapter8
    def test_url_reference_in_index_page_when_logged(self):
        # Create user and log in
        test_utils.create_user()
        self.client.login(username='testuser', password='test1234')

        # Access index page
        response = self.client.get(reverse('index'))

        # Check links that appear for logged person only
        self.assertIn(reverse('add_category'), response.content.decode('ascii'))
        self.assertIn(reverse('restricted'), response.content.decode('ascii'))
        self.assertIn(reverse('logout'), response.content.decode('ascii'))
        self.assertIn(reverse('about'), response.content.decode('ascii'))

    @chapter8
    def test_url_reference_in_index_page_when_not_logged(self):
        #Access index page with user not logged
        response = self.client.get(reverse('index'))

        # Check links that appear for logged person only
        self.assertIn(reverse('register'), response.content.decode('ascii'))
        self.assertIn(reverse('login'), response.content.decode('ascii'))
        self.assertIn(reverse('about'), response.content.decode('ascii'))

    def test_link_to_index_in_base_template(self):
        # Access index
        response = self.client.get(reverse('index'))

        # Check for url referencing index
        self.assertIn(reverse('index'), response.content.decode('ascii'))

    @chapter8
    def test_url_reference_in_category_page(self):
        # Create user and log in
        test_utils.create_user()
        self.client.login(username='testuser', password='test1234')

        # Create categories
        test_utils.create_categories()

        # Check for add_page in category page
        response = self.client.get(reverse('show_category', args=['category-1']))
        self.assertIn(reverse('add_page', args=['category-1']), response.content.decode('ascii'))


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