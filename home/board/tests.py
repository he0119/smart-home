from django.contrib.auth import get_user_model
from django.test import TestCase
from graphql_jwt.testcases import JSONWebTokenTestCase

from .models import Comment, Topic


class ModelTests(TestCase):
    fixtures = ['users', 'board']

    def test_topic_str(self):
        topic = Topic.objects.get(pk=1)

        self.assertEqual(str(topic), 'Hello World!')

    def test_comment_str(self):
        comment = Comment.objects.get(pk=1)

        self.assertEqual(str(comment), 'testcomment1')


class TopicTests(JSONWebTokenTestCase):
    fixtures = ['users', 'board', 'push_disabled']

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
        self.assertEqual(set(titles), {'Hello World!', 'Closed Topic'})

    def test_get_topics_with_number(self):
        """ 测试获取指定数量的话题 """
        query = '''
            query topics($number: Int!) {
                topics(number: $number) {
                    title
                }
            }
        '''
        variables = {'number': 1}

        content = self.client.execute(query, variables)
        self.assertIsNone(content.errors)

        titles = [item['title'] for item in content.data['topics']]
        self.assertEqual(set(titles), {'Hello World!'})

    def test_get_topic(self):
        helloworld = Topic.objects.get(title='Hello World!')

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
                        isOpen
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
        self.assertEqual(topic['isOpen'], True)

    def test_delete_topic(self):
        mutation = '''
            mutation deleteTopic($input: DeleteTopicInput!) {
                deleteTopic(input: $input) {
                    deletedId
                }
            }
        '''

        helloworld = Topic.objects.get(title='Hello World!')
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
            Topic.objects.get(title='Hello World!')

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
        self.assertEqual(old_topic.title, 'Hello World!')

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)
        topic = content.data['updateTopic']['topic']

        self.assertEqual(topic['__typename'], 'TopicType')
        self.assertEqual(topic['id'], '1')
        self.assertEqual(topic['title'], 'test')
        self.assertEqual(topic['description'], 'some')

    def test_close_topic(self):
        mutation = '''
            mutation closeTopic($input: CloseTopicInput!) {
                closeTopic(input: $input) {
                    topic {
                        __typename
                        id
                        isOpen
                    }
                }
            }
        '''
        variables = {
            'input': {
                'topicId': 1,
            }
        }

        old_topic = Topic.objects.get(pk=1)
        self.assertEqual(old_topic.title, 'Hello World!')
        self.assertEqual(old_topic.is_open, True)

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)
        topic = content.data['closeTopic']['topic']

        self.assertEqual(topic['__typename'], 'TopicType')
        self.assertEqual(topic['id'], '1')
        self.assertEqual(topic['isOpen'], False)

    def test_reopen_topic(self):
        mutation = '''
            mutation reopenTopic($input: ReopenTopicInput!) {
                reopenTopic(input: $input) {
                    topic {
                        __typename
                        id
                        title
                        isOpen
                    }
                }
            }
        '''

        variables = {
            'input': {
                'topicId': 2,
            }
        }

        old_topic = Topic.objects.get(pk=2)
        self.assertEqual(old_topic.title, 'Closed Topic')
        self.assertEqual(old_topic.is_open, False)

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)
        topic = content.data['reopenTopic']['topic']

        self.assertEqual(topic['__typename'], 'TopicType')
        self.assertEqual(topic['id'], '2')
        self.assertEqual(topic['title'], 'Closed Topic')
        self.assertEqual(topic['isOpen'], True)

    def test_delete_topic_not_exist(self):
        mutation = '''
            mutation deleteTopic($input: DeleteTopicInput!) {
                deleteTopic(input: $input) {
                    deletedId
                }
            }
        '''

        variables = {
            'input': {
                'topicId': 0,
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '话题不存在')

    def test_update_topic_not_exist(self):
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
                'id': 0,
                'title': 'test',
                'description': 'some',
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '话题不存在')

    def test_close_topic_not_exist(self):
        mutation = '''
            mutation closeTopic($input: CloseTopicInput!) {
                closeTopic(input: $input) {
                    topic {
                        __typename
                        id
                        isOpen
                    }
                }
            }
        '''
        variables = {
            'input': {
                'topicId': 0,
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '话题不存在')

    def test_reopen_topic_not_exist(self):
        mutation = '''
            mutation reopenTopic($input: ReopenTopicInput!) {
                reopenTopic(input: $input) {
                    topic {
                        __typename
                        id
                        title
                        isOpen
                    }
                }
            }
        '''

        variables = {
            'input': {
                'topicId': 0,
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '话题不存在')


class CommentTests(JSONWebTokenTestCase):
    fixtures = ['users', 'board', 'push_disabled']

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
        self.assertEqual(
            set(comments),
            {'testcomment1', 'testcomment2', 'replytotestcomment1'})

    def test_get_comments_with_number(self):
        query = '''
            query comments($topicId: ID!, $number: Int) {
                comments(topicId: $topicId, number: $number) {
                    body
                }
            }
        '''

        variables = {'topicId': 1, 'number': 1}

        content = self.client.execute(query, variables)
        self.assertIsNone(content.errors)
        comments = [item['body'] for item in content.data['comments']]
        self.assertEqual(set(comments), {'testcomment1'})

    def test_get_comments_not_exist(self):
        """ 测试话题不存在的情况 """
        query = '''
            query comments($topicId: ID!) {
                comments(topicId: $topicId) {
                    body
                }
            }
        '''

        variables = {'topicId': 3}

        content = self.client.execute(query, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '话题不存在')

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

    def test_add_comment_with_parent_id(self):
        mutation = '''
            mutation addComment($input: AddCommentInput!) {
                addComment(input: $input) {
                    comment {
                        __typename
                        id
                        body
                        parent {
                            id
                        }
                        replyTo {
                            username
                        }
                    }
                }
            }
        '''
        variables = {
            'input': {
                'topicId': 1,
                'body': 'replytotest2',
                'parentId': 3,
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)

        comment = content.data['addComment']['comment']
        self.assertEqual(comment['__typename'], 'CommentType')
        self.assertEqual(comment['body'], 'replytotest2')
        self.assertEqual(comment['parent']['id'], '1')
        self.assertEqual(comment['replyTo']['username'], 'test2')

    def test_delete_comment(self):
        mutation = '''
            mutation deleteComment($input: DeleteCommentInput!) {
                deleteComment(input: $input) {
                    deletedId
                }
            }
        '''

        test_comment = Comment.objects.get(body='testcomment1')
        variables = {
            'input': {
                'commentId': test_comment.id,
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)

        deletedId = content.data['deleteComment']['deletedId']
        self.assertEqual(deletedId, str(test_comment.id))
        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(body='testcomment1')

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
        self.assertEqual(old_comment.body, 'testcomment1')

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)
        comment = content.data['updateComment']['comment']

        self.assertEqual(comment['__typename'], 'CommentType')
        self.assertEqual(comment['id'], '1')
        self.assertEqual(comment['body'], 'hello')

    def test_add_comment_not_exist(self):
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
                'topicId': 0,
                'body': 'test',
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '话题不存在')

    def test_delete_comment_not_exist(self):
        mutation = '''
            mutation deleteComment($input: DeleteCommentInput!) {
                deleteComment(input: $input) {
                    deletedId
                }
            }
        '''

        variables = {
            'input': {
                'commentId': 0,
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '评论不存在')

    def test_update_comment_not_exist(self):
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
                'id': 0,
                'body': 'hello',
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '评论不存在')


class DifferentUserTopicTests(JSONWebTokenTestCase):
    """ 测试用户操作其他用户创建的东西 """
    fixtures = ['users', 'board', 'push_disabled']

    def setUp(self):
        self.user = get_user_model().objects.get(username='test2')
        self.client.authenticate(self.user)

    def test_delete_topic(self):
        mutation = '''
            mutation deleteTopic($input: DeleteTopicInput!) {
                deleteTopic(input: $input) {
                    deletedId
                }
            }
        '''

        variables = {
            'input': {
                'topicId': 1,
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '只能删除自己创建的话题')

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

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '只能修改自己创建的话题')

    def test_close_topic(self):
        mutation = '''
            mutation closeTopic($input: CloseTopicInput!) {
                closeTopic(input: $input) {
                    topic {
                        __typename
                        id
                        isOpen
                    }
                }
            }
        '''
        variables = {
            'input': {
                'topicId': 1,
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '只能修改自己创建的话题')

    def test_reopen_topic(self):
        mutation = '''
            mutation reopenTopic($input: ReopenTopicInput!) {
                reopenTopic(input: $input) {
                    topic {
                        __typename
                        id
                        title
                        isOpen
                    }
                }
            }
        '''

        variables = {
            'input': {
                'topicId': 1,
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '只能修改自己创建的话题')


class DifferentUserCommentTests(JSONWebTokenTestCase):
    """ 测试用户操作其他用户创建的东西 """
    fixtures = ['users', 'board', 'push_disabled']

    def setUp(self):
        self.user = get_user_model().objects.get(username='test2')
        self.client.authenticate(self.user)

    def test_delete_comment(self):
        mutation = '''
            mutation deleteComment($input: DeleteCommentInput!) {
                deleteComment(input: $input) {
                    deletedId
                }
            }
        '''

        variables = {
            'input': {
                'commentId': 1,
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '只能删除自己创建的评论')

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

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '只能修改自己创建的评论')
