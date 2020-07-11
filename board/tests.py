from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from graphql_jwt.testcases import JSONWebTokenTestCase

from .models import Comment, Topic


def query_set_to_list(query_set):
    """ 转换 TreeQuerySet 到列表 """
    return [i for i in query_set]


class TopicTests(JSONWebTokenTestCase):
    fixtures = ['user', 'board']

    def setUp(self):
        self.user = get_user_model().objects.get(username='test')
        self.client.authenticate(self.user)

    def test_get_topics(self):
        query = '''
            query topics {
                topics {
                    title
                }
            }
        '''
        content = self.client.execute(query)
        self.assertIsNone(content.errors)
        titles = [item['title'] for item in content.data['topics']]
        self.assertEqual(set(titles), set(['你好世界']))

    def test_get_topic(self):
        helloworld = Topic.objects.get(title='你好世界')

        query = f'''
            query topic {{
                topic(id: {helloworld.id}) {{
                    title
                }}
            }}
        '''
        content = self.client.execute(query)
        self.assertIsNone(content.errors)

        title = content.data['topic']['title']
        self.assertEqual(title, helloworld.title)

    def test_add_topic(self):
        mutation = '''
            mutation addTopic($input: AddTopicInput!) {
                addTopic(input: $input) {
                    topic {
                        __typename
                        title
                        description
                    }
                }
            }
        '''
        variables = {
            'input': {
                'title': 'test',
                'description': 'some',
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)

        topic = content.data['addTopic']['topic']
        self.assertEqual(topic['__typename'], 'TopicType')
        self.assertEqual(topic['title'], 'test')
        self.assertEqual(topic['description'], 'some')

    def test_delete_topic(self):
        mutation = '''
            mutation deleteTopic($input: DeleteTopicInput!) {
                deleteTopic(input: $input) {
                    deletedId
                }
            }
        '''

        helloworld = Topic.objects.get(title='你好世界')
        variables = {
            'input': {
                'topicId': helloworld.id,
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)

        deletedId = content.data['deleteTopic']['deletedId']
        self.assertEqual(deletedId, str(helloworld.id))
        with self.assertRaises(Topic.DoesNotExist):
            Topic.objects.get(title='你好世界')

    def test_update_topic(self):
        mutation = '''
            mutation updateTopic($input: UpdateTopicInput!) {
                updateTopic(input: $input) {
                    topic {
                        __typename
                        id
                        title
                        description
                    }
                }
            }
        '''
        variables = {
            'input': {
                'id': 1,
                'title': 'test',
                'description': 'some',
            }
        }

        old_topic = Topic.objects.get(pk=1)
        self.assertEqual(old_topic.title, '你好世界')

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)
        topic = content.data['updateTopic']['topic']

        self.assertEqual(topic['__typename'], 'TopicType')
        self.assertEqual(topic['id'], '1')
        self.assertEqual(topic['title'], 'test')
        self.assertEqual(topic['description'], 'some')


class CommentTests(JSONWebTokenTestCase):
    fixtures = ['user', 'board']

    def setUp(self):
        self.user = get_user_model().objects.get(username='test')
        self.client.authenticate(self.user)

    def test_get_comments(self):
        query = '''
            query comments($topicId: ID!) {
                comments(topicId: $topicId) {
                    body
                }
            }
        '''

        variables = {'topicId': 1}

        content = self.client.execute(query, variables)
        self.assertIsNone(content.errors)
        comments = [item['body'] for item in content.data['comments']]
        self.assertEqual(set(comments), set(['你好！']))

    def test_add_comment(self):
        mutation = '''
            mutation addComment($input: AddCommentInput!) {
                addComment(input: $input) {
                    comment {
                        __typename
                        id
                        body
                    }
                }
            }
        '''
        variables = {
            'input': {
                'topicId': 1,
                'body': 'test',
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)

        comment = content.data['addComment']['comment']
        self.assertEqual(comment['__typename'], 'CommentType')
        self.assertEqual(comment['body'], 'test')

    def test_delete_comment(self):
        mutation = '''
            mutation deleteComment($input: DeleteCommentInput!) {
                deleteComment(input: $input) {
                    deletedId
                }
            }
        '''

        hello = Comment.objects.get(body='你好！')
        variables = {
            'input': {
                'commentId': hello.id,
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)

        deletedId = content.data['deleteComment']['deletedId']
        self.assertEqual(deletedId, str(hello.id))
        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(body='你好！')

    def test_update_comment(self):
        mutation = '''
            mutation updateComment($input: UpdateCommentInput!) {
                updateComment(input: $input) {
                    comment {
                        __typename
                        id
                        body
                    }
                }
            }
        '''
        variables = {
            'input': {
                'id': 1,
                'body': 'hello',
            }
        }

        old_comment = Comment.objects.get(pk=1)
        self.assertEqual(old_comment.body, '你好！')

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)
        comment = content.data['updateComment']['comment']

        self.assertEqual(comment['__typename'], 'CommentType')
        self.assertEqual(comment['id'], '1')
        self.assertEqual(comment['body'], 'hello')
