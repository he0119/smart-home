from django.contrib.auth import get_user_model
from django.test import TestCase
from graphql_jwt.testcases import JSONWebTokenTestCase
from graphql_relay import to_global_id

from .models import Comment, Topic
from .utils import unmark


class ModelTests(TestCase):
    fixtures = ['users', 'board']

    def test_topic_str(self):
        topic = Topic.objects.get(pk=1)

        self.assertEqual(str(topic), '你好世界')

    def test_comment_str(self):
        comment = Comment.objects.get(pk=1)

        self.assertEqual(str(comment), '测试评论一')


class TopicTests(JSONWebTokenTestCase):
    fixtures = ['users', 'board', 'push_disabled']

    def setUp(self):
        self.user = get_user_model().objects.get(username='test')
        self.client.authenticate(self.user)

    def test_get_topic(self):
        """ 通过 Node 来获得指定话题 """
        helloworld = Topic.objects.get(title='你好世界')
        global_id = to_global_id('TopicType', helloworld.id)

        query = f'''
            query node {{
                node(id: "{global_id}") {{
                    ... on TopicType {{
                        title
                        comments(first: 1) {{
                            edges {{
                                node {{
                                    body
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        '''
        content = self.client.execute(query)
        self.assertIsNone(content.errors)

        title = content.data['node']['title']
        self.assertEqual(title, helloworld.title)
        comments = [
            item['node']['body']
            for item in content.data['node']['comments']['edges']
        ]
        self.assertEqual(set(comments), {'测试评论一'})

    def test_get_topics(self):
        """ 获取所有话题 """
        query = '''
            query topics {
                topics(first: 2) {
                    edges {
                        node {
                            title
                        }
                    }
                }
            }
        '''
        content = self.client.execute(query)
        self.assertIsNone(content.errors)

        titles = [
            item['node']['title'] for item in content.data['topics']['edges']
        ]
        self.assertEqual(set(titles), {'你好世界', '关闭的话题'})

    def test_get_frist_topics(self):
        """ 获取最近活动的一个话题 """
        query = '''
            query topics {
                topics(first: 1, orderBy: "-active_at") {
                    edges {
                        node {
                            title
                        }
                    }
                }
            }
        '''
        content = self.client.execute(query)
        self.assertIsNone(content.errors)

        titles = [
            topic['node']['title'] for topic in content.data['topics']['edges']
        ]
        self.assertEqual(set(titles), {'你好世界'})

    def test_get_pinned_topics(self):
        """ 获取置顶的一个话题 """
        query = '''
            query topics {
                topics(first: 1, orderBy: "-is_pin") {
                    edges {
                        node {
                            title
                        }
                    }
                }
            }
        '''
        content = self.client.execute(query)
        self.assertIsNone(content.errors)

        titles = [
            topic['node']['title'] for topic in content.data['topics']['edges']
        ]
        self.assertEqual(set(titles), {'置顶的话题'})

    def test_add_topic(self):
        mutation = '''
            mutation addTopic($input: AddTopicMutationInput!) {
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
            mutation deleteTopic($input: DeleteTopicMutationInput!) {
                deleteTopic(input: $input) {
                    __typename
                }
            }
        '''

        helloworld = Topic.objects.get(title='你好世界')
        variables = {
            'input': {
                'topicId': to_global_id('TopicType', helloworld.id),
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)

        typename = content.data['deleteTopic']['__typename']
        self.assertEqual(typename, 'DeleteTopicMutationPayload')
        with self.assertRaises(Topic.DoesNotExist):
            Topic.objects.get(title='你好世界')

    def test_update_topic(self):
        mutation = '''
            mutation updateTopic($input: UpdateTopicMutationInput!) {
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
                'id': to_global_id('TopicType', '1'),
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
        self.assertEqual(topic['id'], to_global_id('TopicType', '1'))
        self.assertEqual(topic['title'], 'test')
        self.assertEqual(topic['description'], 'some')

    def test_close_topic(self):
        mutation = '''
            mutation closeTopic($input: CloseTopicMutationInput!) {
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
                'topicId': to_global_id('TopicType', '1'),
            }
        }

        old_topic = Topic.objects.get(pk=1)
        self.assertEqual(old_topic.title, '你好世界')
        self.assertEqual(old_topic.is_open, True)

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)
        topic = content.data['closeTopic']['topic']

        self.assertEqual(topic['__typename'], 'TopicType')
        self.assertEqual(topic['id'], to_global_id('TopicType', '1'))
        self.assertEqual(topic['isOpen'], False)

    def test_reopen_topic(self):
        mutation = '''
            mutation reopenTopic($input: ReopenTopicMutationInput!) {
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
                'topicId': to_global_id('TopicType', '2'),
            }
        }

        old_topic = Topic.objects.get(pk=2)
        self.assertEqual(old_topic.title, '关闭的话题')
        self.assertEqual(old_topic.is_open, False)

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)
        topic = content.data['reopenTopic']['topic']

        self.assertEqual(topic['__typename'], 'TopicType')
        self.assertEqual(topic['id'], to_global_id('TopicType', '2'))
        self.assertEqual(topic['title'], '关闭的话题')
        self.assertEqual(topic['isOpen'], True)

    def test_delete_topic_not_exist(self):
        mutation = '''
            mutation deleteTopic($input: DeleteTopicMutationInput!) {
                deleteTopic(input: $input) {
                    __typename
                }
            }
        '''

        variables = {
            'input': {
                'topicId': to_global_id('TopicType', '0'),
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '话题不存在')

    def test_update_topic_not_exist(self):
        mutation = '''
            mutation updateTopic($input: UpdateTopicMutationInput!) {
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
                'id': to_global_id('TopicType', '0'),
                'title': 'test',
                'description': 'some',
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '话题不存在')

    def test_close_topic_not_exist(self):
        mutation = '''
            mutation closeTopic($input: CloseTopicMutationInput!) {
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
                'topicId': to_global_id('TopicType', '0'),
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '话题不存在')

    def test_reopen_topic_not_exist(self):
        mutation = '''
            mutation reopenTopic($input: ReopenTopicMutationInput!) {
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
                'topicId': to_global_id('TopicType', '0'),
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '话题不存在')

    def test_pin_topic(self):
        mutation = '''
            mutation pinTopic($input: PinTopicMutationInput!) {
                pinTopic(input: $input) {
                    topic {
                        __typename
                        id
                        isPin
                    }
                }
            }
        '''
        old_topic = Topic.objects.get(pk=1)
        self.assertEqual(old_topic.is_pin, False)

        variables = {
            'input': {
                'topicId': to_global_id('TopicType', old_topic.id),
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)

        topic = content.data['pinTopic']['topic']

        self.assertEqual(topic['__typename'], 'TopicType')
        self.assertEqual(topic['id'], to_global_id('TopicType', old_topic.id))
        self.assertEqual(topic['isPin'], True)

    def test_unpin_topic(self):
        mutation = '''
            mutation unpinTopic($input: UnpinTopicMutationInput!) {
                unpinTopic(input: $input) {
                    topic {
                        __typename
                        id
                        title
                        isPin
                    }
                }
            }
        '''
        old_topic = Topic.objects.get(pk=3)

        variables = {
            'input': {
                'topicId': to_global_id('TopicType', old_topic.id),
            }
        }

        self.assertEqual(old_topic.is_pin, True)

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)
        topic = content.data['unpinTopic']['topic']

        self.assertEqual(topic['__typename'], 'TopicType')
        self.assertEqual(topic['id'], to_global_id('TopicType', old_topic.id))
        self.assertEqual(topic['isPin'], False)

    def test_pin_topic_not_exist(self):
        mutation = '''
            mutation pinTopic($input: PinTopicMutationInput!) {
                pinTopic(input: $input) {
                    topic {
                        __typename
                        id
                        isPin
                    }
                }
            }
        '''
        variables = {
            'input': {
                'topicId': to_global_id('TopicType', '0'),
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '话题不存在')

    def test_unpin_topic_not_exist(self):
        mutation = '''
            mutation unpinTopic($input: UnpinTopicMutationInput!) {
                unpinTopic(input: $input) {
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
                'topicId': to_global_id('TopicType', '0'),
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

    def test_get_comment(self):
        """ 通过 Node 来获得指定评论 """
        test_comment = Comment.objects.get(body='测试评论一')
        global_id = to_global_id('CommentType', test_comment.id)

        query = f'''
            query node {{
                node(id: "{global_id}") {{
                    ... on CommentType {{
                        body
                    }}
                }}
            }}
        '''
        content = self.client.execute(query)
        self.assertIsNone(content.errors)

        body = content.data['node']['body']
        self.assertEqual(body, test_comment.body)

    def test_get_comments(self):
        query = '''
            query comments {
                comments {
                    edges {
                        node {
                            body
                        }
                    }
                }
            }
        '''

        content = self.client.execute(query)
        self.assertIsNone(content.errors)
        comments = [
            item['node']['body'] for item in content.data['comments']['edges']
        ]
        self.assertEqual(set(comments), {'测试评论一', '测试评论二', '评论测试评论一'})

    def test_get_first_comments(self):
        query = '''
            query comments {
                comments(first: 1) {
                    edges {
                        node {
                            body
                        }
                    }
                }
            }
        '''

        content = self.client.execute(query)
        self.assertIsNone(content.errors)

        comments = [
            item['node']['body'] for item in content.data['comments']['edges']
        ]
        self.assertEqual(set(comments), {'测试评论一'})

    def test_add_comment(self):
        mutation = '''
            mutation addComment($input: AddCommentMutationInput!) {
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
                'topicId': to_global_id('TopicType', '1'),
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
            mutation addComment($input: AddCommentMutationInput!) {
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
                'topicId': to_global_id('TopicType', '1'),
                'body': '测试评论给测试评论二',
                'parentId': to_global_id('CommentType', '3'),
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)

        comment = content.data['addComment']['comment']
        self.assertEqual(comment['__typename'], 'CommentType')
        self.assertEqual(comment['body'], '测试评论给测试评论二')
        self.assertEqual(comment['parent']['id'],
                         to_global_id('CommentType', '1'))
        self.assertEqual(comment['replyTo']['username'], 'test2')

    def test_delete_comment(self):
        mutation = '''
            mutation deleteComment($input: DeleteCommentMutationInput!) {
                deleteComment(input: $input) {
                    __typename
                }
            }
        '''

        test_comment = Comment.objects.get(body='测试评论一')
        variables = {
            'input': {
                'commentId': to_global_id('CommentType', test_comment.id),
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)

        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(body='测试评论一')

    def test_update_comment(self):
        mutation = '''
            mutation updateComment($input: UpdateCommentMutationInput!) {
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
                'id': to_global_id('CommentType', '1'),
                'body': 'hello',
            }
        }

        old_comment = Comment.objects.get(pk=1)
        self.assertEqual(old_comment.body, '测试评论一')

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)
        comment = content.data['updateComment']['comment']

        self.assertEqual(comment['__typename'], 'CommentType')
        self.assertEqual(comment['id'], to_global_id('CommentType', '1'))
        self.assertEqual(comment['body'], 'hello')

    def test_add_comment_not_exist(self):
        mutation = '''
            mutation addComment($input: AddCommentMutationInput!) {
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
                'topicId': to_global_id('TopicType', '0'),
                'body': 'test',
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '话题不存在')

    def test_delete_comment_not_exist(self):
        mutation = '''
            mutation deleteComment($input: DeleteCommentMutationInput!) {
                deleteComment(input: $input) {
                    __typename
                }
            }
        '''

        variables = {
            'input': {
                'commentId': to_global_id('CommentType', '0'),
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '评论不存在')

    def test_update_comment_not_exist(self):
        mutation = '''
            mutation updateComment($input: UpdateCommentMutationInput!) {
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
                'id': to_global_id('CommentType', '0'),
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
            mutation deleteTopic($input: DeleteTopicMutationInput!) {
                deleteTopic(input: $input) {
                    __typename
                }
            }
        '''

        variables = {
            'input': {
                'topicId': to_global_id('TopicType', '1'),
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '只能删除自己创建的话题')

    def test_update_topic(self):
        mutation = '''
            mutation updateTopic($input: UpdateTopicMutationInput!) {
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
                'id': to_global_id('TopicType', '1'),
                'title': 'test',
                'description': 'some',
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '只能修改自己创建的话题')

    def test_close_topic(self):
        mutation = '''
            mutation closeTopic($input: CloseTopicMutationInput!) {
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
                'topicId': to_global_id('TopicType', '1'),
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '只能修改自己创建的话题')

    def test_reopen_topic(self):
        mutation = '''
            mutation reopenTopic($input: ReopenTopicMutationInput!) {
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
                'topicId': to_global_id('TopicType', '1'),
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
            mutation deleteComment($input: DeleteCommentMutationInput!) {
                deleteComment(input: $input) {
                    __typename
                }
            }
        '''

        variables = {
            'input': {
                'commentId': to_global_id('CommentType', '1'),
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '只能删除自己创建的评论')

    def test_update_comment(self):
        mutation = '''
            mutation updateComment($input: UpdateCommentMutationInput!) {
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
                'id': to_global_id('CommentType', '1'),
                'body': 'hello',
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '只能修改自己创建的评论')


class MarkdownTests(TestCase):
    def test_unmark(self):
        markdown = '# 标题\n\n- 列表一\n- 列表二'

        plaintext = unmark(markdown)

        self.assertEqual(plaintext, '标题\n\n列表一\n列表二')

    def test_unmark_url(self):
        markdown = '# 标题\n\n- 列表一\n- [列表二](https://test.com)'

        plaintext = unmark(markdown)

        self.assertEqual(plaintext, '标题\n\n列表一\n列表二')
