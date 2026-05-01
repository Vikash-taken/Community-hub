from django.test import TestCase

from .models import Comment, Community, Post, User, Vote


class NetworkTestCase(TestCase):

    def setUp(self):
        # creating user
        self.user1 = User.objects.create_user(
            username="vikash", email="vikash@gmail.com", password="1234"
        )
        self.user2 = User.objects.create_user(
            username="om", email="om@gmail.com", password="123"
        )

        # creating community
        self.comm1 = Community.objects.create(
            name="fun",
            description="Small little fun group, be respectable and have fun",
        )
        self.comm2 = Community.objects.create(
            name="study",
            description="This community is made for heping out those who cannot afford expensive lecture or books",
        )

        # creating post
        self.p1 = Post.objects.create(
            title="Blender Course files",
            content="Most the blender course are the free to download via link provided below(course like alive, rigging or many more)",
            url="Never/goona/give/you/up",
            user=self.user2,
            community=self.comm2,
        )
        self.p2 = Post.objects.create(
            title="Macbook repair",
            content="Guys can you believe it i got my macbook repaired at price of 8,900",
            user=self.user2,
            community=self.comm1,
        )

        # creatin comment
        self.c1 = Comment.objects.create(
            text="Wow thank you so much for the courses you are life saver",
            user=self.user1,
            post=self.p1,
        )
        self.c2 = Comment.objects.create(
            text="I hope you liked it",
            user=self.user2,
            post=self.p1,
            parent=self.c1,
        )

        # creating vote
        self.v1 = Vote.objects.create(direction=1, post=self.p1, user=self.user1)
        self.v2 = Vote.objects.create(direction=1, comment=self.c1, user=self.user2)
        self.v3 = Vote.objects.create(direction=-1, post=self.p2, user=self.user1)

    def test_user_model_count(self):
        self.assertEqual(User.objects.count(), 2)

    def test_community_model_count(self):
        self.assertEqual(Community.objects.count(), 2)

    def test_post_count(self):
        self.assertEqual(Post.objects.count(), 2)

    def test_comment_count(self):
        self.assertEqual(Comment.objects.count(), 2)

    def test_vote_unique_constraint(self):
        self.assertEqual(Vote.objects.count(), 3)

        self.assertEqual(Vote.objects.filter(post=self.p1, user=self.user1).count(), 1)
        Vote.objects.create(direction=-1, post=self.p2, user=self.user2)
        self.assertEqual(Vote.objects.count(), 4)
        Vote.objects.create(direction=1, comment=self.c1, user=self.user2)
        self.assertEqual(Vote.objects.count(), 3)
        self.assertFalse(Vote.objects.filter(comment=self.c1, user=self.user2).exists())
        v4 = Vote.objects.create(direction=-1, post=self.p1, user=self.user2)
        self.assertIsNotNone(v4.pk)
        self.assertEqual(Vote.objects.count(), 4)
