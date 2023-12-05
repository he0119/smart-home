from django.contrib.auth import get_user_model
from django.test import TestCase
from strawberry import relay

from home.tests import GraphQLTestCase

from . import types
from .models import Comment, Topic
from .utils import unmark


class ModelTests(TestCase):
    fixtures = ["users", "board"]

    def test_topic_str(self):
        topic = Topic.objects.get(pk=1)

        self.assertEqual(str(topic), "你好世界")

    def test_comment_str(self):
        comment = Comment.objects.get(pk=1)

        self.assertEqual(str(comment), "测试评论一")


class TopicTests(GraphQLTestCase):
    fixtures = ["users", "board", "push_disabled"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="test")
        self.client.authenticate(self.user)

    def test_get_topic(self):
        """获得指定话题"""
        helloworld = Topic.objects.get(title="你好世界")

        query = """
            query topic($id: GlobalID!) {
                topic(id: $id) {
                    title
                    comments(first: 1, filters: {}, order: {}) {
                        edges {
                            node {
                                body
                            }
                        }
                    }
                }
            }
        """
        variables = {
            "id": relay.to_base64(types.Topic, helloworld.id),
        }

        content = self.client.execute(query, variables)

        title = content.data["topic"]["title"]
        self.assertEqual(title, helloworld.title)
        comments = [
            item["node"]["body"] for item in content.data["topic"]["comments"]["edges"]
        ]
        self.assertEqual(set(comments), {"测试评论一"})

    def test_get_topics(self):
        """获取所有话题"""
        query = """
            query topics {
                topics(first: 2) {
                    edges {
                        node {
                            title
                            user {
                                avatarUrl
                            }
                        }
                    }
                }
            }
        """
        content = self.client.execute(query)

        titles = [item["node"]["title"] for item in content.data["topics"]["edges"]]
        self.assertEqual(set(titles), {"你好世界", "关闭的话题"})

    def test_get_frist_topics(self):
        """获取最近活动的一个话题"""
        query = """
            query topics {
                topics(first: 1, order: {activeAt: DESC}) {
                    edges {
                        node {
                            title
                        }
                    }
                }
            }
        """
        content = self.client.execute(query)

        titles = [topic["node"]["title"] for topic in content.data["topics"]["edges"]]
        self.assertEqual(set(titles), {"你好世界"})

    def test_get_pinned_topics(self):
        """获取置顶的一个话题"""
        query = """
            query topics {
                topics(first: 1, order: {isPinned: DESC}) {
                    edges {
                        node {
                            title
                        }
                    }
                }
            }
        """
        content = self.client.execute(query)

        titles = [topic["node"]["title"] for topic in content.data["topics"]["edges"]]
        self.assertEqual(set(titles), {"置顶的话题"})

    def test_add_topic(self):
        mutation = """
            mutation addTopic($input: AddTopicInput!) {
                addTopic(input: $input) {
                    ... on Topic {
                        __typename
                        title
                        description
                        isClosed
                    }
                }
            }
        """
        variables = {
            "input": {
                "title": "test",
                "description": "some",
            }
        }

        content = self.client.execute(mutation, variables)

        topic = content.data["addTopic"]
        self.assertEqual(topic["__typename"], "Topic")
        self.assertEqual(topic["title"], "test")
        self.assertEqual(topic["description"], "some")
        self.assertEqual(topic["isClosed"], False)

    def test_delete_topic(self):
        """删除话题"""
        mutation = """
            mutation deleteTopic($input: DeleteTopicInput!) {
                deleteTopic(input: $input) {
                    __typename
                }
            }
        """

        helloworld = Topic.objects.get(title="你好世界")
        variables = {
            "input": {
                "topicId": relay.to_base64(types.Topic, helloworld.id),
            }
        }

        content = self.client.execute(mutation, variables)

        typename = content.data["deleteTopic"]["__typename"]
        self.assertEqual(typename, "Topic")
        with self.assertRaises(Topic.DoesNotExist):
            Topic.objects.get(title="你好世界")

    def test_delete_closed_topic(self):
        """删除已关闭的话题"""
        mutation = """
            mutation deleteTopic($input: DeleteTopicInput!) {
                deleteTopic(input: $input) {
                    ... on OperationInfo {
                        __typename
                        messages {
                            message
                        }
                    }
                }
            }
        """

        helloworld = Topic.objects.get(pk=2)
        variables = {
            "input": {
                "topicId": relay.to_base64(types.Topic, helloworld.id),
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["deleteTopic"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "不能删除已关闭的话题")

    def test_update_topic(self):
        """更新话题"""
        mutation = """
            mutation updateTopic($input: UpdateTopicInput!) {
                updateTopic(input: $input) {
                    ... on Topic {
                        __typename
                        id
                        title
                        description
                    }
                }
            }
        """
        variables = {
            "input": {
                "id": relay.to_base64(types.Topic, "1"),
                "title": "test",
                "description": "some",
            }
        }

        old_topic = Topic.objects.get(pk=1)
        self.assertEqual(old_topic.title, "你好世界")

        content = self.client.execute(mutation, variables)

        topic = content.data["updateTopic"]
        self.assertEqual(topic["__typename"], "Topic")
        self.assertEqual(topic["id"], relay.to_base64(types.Topic, "1"))
        self.assertEqual(topic["title"], "test")
        self.assertEqual(topic["description"], "some")

    def test_update_closed_topic(self):
        """更新已关闭的话题"""
        mutation = """
            mutation updateTopic($input: UpdateTopicInput!) {
                updateTopic(input: $input) {
                    ... on OperationInfo {
                        __typename
                        messages {
                            message
                        }
                    }
                }
            }
        """
        variables = {
            "input": {
                "id": relay.to_base64(types.Topic, "2"),
                "title": "test",
                "description": "some",
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["updateTopic"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "不能修改已关闭的话题")

    def test_close_topic(self):
        mutation = """
            mutation closeTopic($input: CloseTopicInput!) {
                closeTopic(input: $input) {
                    ... on Topic {
                        __typename
                        id
                        isClosed
                    }
                }
            }
        """
        variables = {
            "input": {
                "topicId": relay.to_base64(types.Topic, "1"),
            }
        }

        old_topic: Topic = Topic.objects.get(pk=1)
        self.assertEqual(old_topic.title, "你好世界")
        self.assertEqual(old_topic.is_closed, False)

        content = self.client.execute(mutation, variables)

        topic = content.data["closeTopic"]
        self.assertEqual(topic["__typename"], "Topic")
        self.assertEqual(topic["id"], relay.to_base64(types.Topic, "1"))
        self.assertEqual(topic["isClosed"], True)

    def test_reopen_topic(self):
        mutation = """
            mutation reopenTopic($input: ReopenTopicInput!) {
                reopenTopic(input: $input) {
                    ... on Topic {
                        __typename
                        id
                        title
                        isClosed
                        closedAt
                    }
                }
            }
        """

        variables = {
            "input": {
                "topicId": relay.to_base64(types.Topic, "2"),
            }
        }

        old_topic: Topic = Topic.objects.get(pk=2)
        self.assertEqual(old_topic.title, "关闭的话题")
        self.assertEqual(old_topic.is_closed, True)
        self.assertIsNotNone(old_topic.closed_at)

        content = self.client.execute(mutation, variables)

        topic = content.data["reopenTopic"]
        self.assertEqual(topic["__typename"], "Topic")
        self.assertEqual(topic["id"], relay.to_base64(types.Topic, "2"))
        self.assertEqual(topic["title"], "关闭的话题")
        self.assertEqual(topic["isClosed"], False)
        self.assertIsNone(topic["closedAt"])

    def test_delete_topic_not_exist(self):
        mutation = """
            mutation deleteTopic($input: DeleteTopicInput!) {
                deleteTopic(input: $input) {
                    ... on OperationInfo {
                        __typename
                        messages {
                            message
                        }
                    }
                }
            }
        """

        variables = {
            "input": {
                "topicId": relay.to_base64(types.Topic, "0"),
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["deleteTopic"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "话题不存在")

    def test_update_topic_not_exist(self):
        mutation = """
            mutation updateTopic($input: UpdateTopicInput!) {
                updateTopic(input: $input) {
                    ... on OperationInfo {
                        __typename
                        messages {
                            message
                        }
                    }
                }
            }
        """
        variables = {
            "input": {
                "id": relay.to_base64(types.Topic, "0"),
                "title": "test",
                "description": "some",
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["updateTopic"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "话题不存在")

    def test_close_topic_not_exist(self):
        mutation = """
            mutation closeTopic($input: CloseTopicInput!) {
                closeTopic(input: $input) {
                    ... on OperationInfo {
                        __typename
                        messages {
                            message
                        }
                    }
                }
            }
        """
        variables = {
            "input": {
                "topicId": relay.to_base64(types.Topic, "0"),
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["closeTopic"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "话题不存在")

    def test_reopen_topic_not_exist(self):
        mutation = """
            mutation reopenTopic($input: ReopenTopicInput!) {
                reopenTopic(input: $input) {
                    ... on OperationInfo {
                        __typename
                        messages {
                            message
                        }
                    }
                }
            }
        """

        variables = {
            "input": {
                "topicId": relay.to_base64(types.Topic, "0"),
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["reopenTopic"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "话题不存在")

    def test_pin_topic(self):
        mutation = """
            mutation pinTopic($input: PinTopicInput!) {
                pinTopic(input: $input) {
                    ... on Topic {
                        __typename
                        id
                        isPinned
                    }
                }
            }
        """
        old_topic = Topic.objects.get(pk=1)
        self.assertEqual(old_topic.is_pinned, False)

        variables = {
            "input": {
                "topicId": relay.to_base64(types.Topic, old_topic.id),
            }
        }

        content = self.client.execute(mutation, variables)

        topic = content.data["pinTopic"]

        self.assertEqual(topic["__typename"], "Topic")
        self.assertEqual(topic["id"], relay.to_base64(types.Topic, old_topic.id))
        self.assertEqual(topic["isPinned"], True)

    def test_unpin_topic(self):
        mutation = """
            mutation unpinTopic($input: UnpinTopicInput!) {
                unpinTopic(input: $input) {
                    ... on Topic {
                        __typename
                        id
                        title
                        isPinned
                    }
                }
            }
        """
        old_topic = Topic.objects.get(pk=3)

        variables = {
            "input": {
                "topicId": relay.to_base64(types.Topic, old_topic.id),
            }
        }

        self.assertEqual(old_topic.is_pinned, True)

        content = self.client.execute(mutation, variables)
        topic = content.data["unpinTopic"]

        self.assertEqual(topic["__typename"], "Topic")
        self.assertEqual(topic["id"], relay.to_base64(types.Topic, old_topic.id))
        self.assertEqual(topic["isPinned"], False)

    def test_pin_topic_not_exist(self):
        mutation = """
            mutation pinTopic($input: PinTopicInput!) {
                pinTopic(input: $input) {
                    ... on OperationInfo {
                        __typename
                        messages {
                            message
                        }
                    }
                }
            }
        """
        variables = {
            "input": {
                "topicId": relay.to_base64(types.Topic, "0"),
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["pinTopic"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "话题不存在")

    def test_unpin_topic_not_exist(self):
        mutation = """
            mutation unpinTopic($input: UnpinTopicInput!) {
                unpinTopic(input: $input) {
                    ... on OperationInfo {
                        __typename
                        messages {
                            message
                        }
                    }
                }
            }
        """

        variables = {
            "input": {
                "topicId": relay.to_base64(types.Topic, "0"),
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["unpinTopic"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "话题不存在")


class CommentTests(GraphQLTestCase):
    fixtures = ["users", "board", "push_disabled"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="test")
        self.client.authenticate(self.user)

    def test_get_comment(self):
        """通过 Node 来获得指定评论"""
        test_comment = Comment.objects.get(body="测试评论一")

        query = """
            query comment($id: GlobalID!) {
                comment(id: $id) {
                    body
                    parent {
                        body
                    }
                    replyTo {
                        username
                    }
                }
            }
        """
        variables = {"id": relay.to_base64(types.Comment, test_comment.id)}
        content = self.client.execute(query, variables)

        body = content.data["comment"]["body"]
        self.assertEqual(body, test_comment.body)

    def test_get_comments(self):
        query = """
            query comments {
                comments {
                    edges {
                        node {
                            body
                        }
                    }
                }
            }
        """

        content = self.client.execute(query)
        comments = [item["node"]["body"] for item in content.data["comments"]["edges"]]
        self.assertEqual(
            set(comments),
            {"测试评论一", "测试评论二", "评论测试评论一", "测试评论关闭的话题"},
        )

    def test_get_comments_by_topic_id(self):
        """测试通过 topicId 来获取评论"""
        query = """
            query comments($topicId: GlobalID!) {
                comments(filters: {topic: {id: $topicId}}) {
                    edges {
                        node {
                            body
                        }
                    }
                }
            }
        """
        variables = {"topicId": relay.to_base64(types.Topic, 2)}

        content = self.client.execute(query, variables)
        comments = [item["node"]["body"] for item in content.data["comments"]["edges"]]
        self.assertEqual(comments, ["测试评论关闭的话题"])

    def test_get_first_comments(self):
        query = """
            query comments {
                comments(first: 1) {
                    edges {
                        node {
                            body
                        }
                    }
                }
            }
        """

        content = self.client.execute(query)

        comments = [item["node"]["body"] for item in content.data["comments"]["edges"]]
        self.assertEqual(set(comments), {"测试评论一"})

    def test_get_last_comments(self):
        query = """
            query topics {
                topics(order: {isPinned: DESC, isClosed: ASC, activeAt: DESC}) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    edges {
                        node {
                            id
                            title
                            description
                            isClosed
                            isPinned
                            createdAt
                            editedAt
                            user {
                            username
                            email
                            }
                            comments(last: 1, after: null) {
                                edges {
                                    node {
                                        body
                                    }
                                }
                            }
                        }
                    }
                }
            }
        """

        content = self.client.execute(query)

        comments = [
            item["node"]["body"]
            for item in content.data["topics"]["edges"][1]["node"]["comments"]["edges"]
        ]
        self.assertEqual(comments, ["测试评论二"])

    def test_add_comment(self):
        mutation = """
            mutation addComment($input: AddCommentInput!) {
                addComment(input: $input) {
                    ... on Comment {
                        __typename
                        id
                        body
                    }
                }
            }
        """
        variables = {
            "input": {
                "topicId": relay.to_base64(types.Topic, "1"),
                "body": "test",
            }
        }

        content = self.client.execute(mutation, variables)

        comment = content.data["addComment"]
        self.assertEqual(comment["__typename"], "Comment")
        self.assertEqual(comment["body"], "test")

    def test_add_comment_with_parent_id(self):
        mutation = """
            mutation addComment($input: AddCommentInput!) {
                addComment(input: $input) {
                    ... on Comment {
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
        """
        variables = {
            "input": {
                "topicId": relay.to_base64(types.Topic, "1"),
                "body": "测试评论给测试评论二",
                "parentId": relay.to_base64(types.Comment, "3"),
            }
        }

        content = self.client.execute(mutation, variables)

        comment = content.data["addComment"]
        self.assertEqual(comment["__typename"], "Comment")
        self.assertEqual(comment["body"], "测试评论给测试评论二")
        self.assertEqual(comment["parent"]["id"], relay.to_base64(types.Comment, "1"))
        self.assertEqual(comment["replyTo"]["username"], "test2")

    def test_add_comment_with_parent_id_not_exist(self):
        """测试回复的评论不存在"""
        mutation = """
            mutation addComment($input: AddCommentInput!) {
                addComment(input: $input) {
                    ... on OperationInfo {
                        __typename
                        messages {
                            message
                        }
                    }
                }
            }
        """
        variables = {
            "input": {
                "topicId": relay.to_base64(types.Topic, "1"),
                "body": "测试评论给测试评论二",
                "parentId": relay.to_base64(types.Comment, "0"),
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["addComment"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "回复的评论不存在")

    def test_delete_comment(self):
        mutation = """
            mutation deleteComment($input: DeleteCommentInput!) {
                deleteComment(input: $input) {
                    __typename
                }
            }
        """

        test_comment = Comment.objects.get(body="测试评论一")
        variables = {
            "input": {
                "commentId": relay.to_base64(types.Comment, test_comment.id),
            }
        }

        self.client.execute(mutation, variables)

        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(body="测试评论一")

    def test_update_comment(self):
        mutation = """
            mutation updateComment($input: UpdateCommentInput!) {
                updateComment(input: $input) {
                    ... on Comment {
                        __typename
                        id
                        body
                    }
                }
            }
        """
        variables = {
            "input": {
                "id": relay.to_base64(types.Comment, "1"),
                "body": "hello",
            }
        }

        old_comment = Comment.objects.get(pk=1)
        self.assertEqual(old_comment.body, "测试评论一")

        content = self.client.execute(mutation, variables)

        comment = content.data["updateComment"]
        self.assertEqual(comment["__typename"], "Comment")
        self.assertEqual(comment["id"], relay.to_base64(types.Comment, "1"))
        self.assertEqual(comment["body"], "hello")

    def test_add_comment_not_exist(self):
        mutation = """
            mutation addComment($input: AddCommentInput!) {
                addComment(input: $input) {
                    ... on OperationInfo {
                        __typename
                        messages {
                            message
                        }
                    }
                }
            }
        """
        variables = {
            "input": {
                "topicId": relay.to_base64(types.Topic, "0"),
                "body": "test",
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["addComment"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "话题不存在")

    def test_add_comment_to_closed_topic(self):
        mutation = """
            mutation addComment($input: AddCommentInput!) {
                addComment(input: $input) {
                    ... on OperationInfo {
                        __typename
                        messages {
                            message
                        }
                    }
                }
            }
        """
        variables = {
            "input": {
                "topicId": relay.to_base64(types.Topic, "2"),
                "body": "test",
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["addComment"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "不能向已关闭话题添加评论")

    def test_delete_comment_in_closed_topic(self):
        mutation = """
            mutation deleteComment($input: DeleteCommentInput!) {
                deleteComment(input: $input) {
                    ... on OperationInfo {
                        __typename
                        messages {
                            message
                        }
                    }
                }
            }
        """

        variables = {
            "input": {
                "commentId": relay.to_base64(types.Comment, "4"),
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["deleteComment"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "不能删除已关闭话题下的评论")

    def test_update_comment_in_closed_topic(self):
        mutation = """
            mutation updateComment($input: UpdateCommentInput!) {
                updateComment(input: $input) {
                    ... on OperationInfo {
                        __typename
                        messages {
                            message
                        }
                    }
                }
            }
        """
        variables = {
            "input": {
                "id": relay.to_base64(types.Comment, "4"),
                "body": "hello",
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["updateComment"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "不能修改已关闭话题下的评论")

    def test_delete_comment_not_exist(self):
        mutation = """
            mutation deleteComment($input: DeleteCommentInput!) {
                deleteComment(input: $input) {
                    ... on OperationInfo {
                        __typename
                        messages {
                            message
                        }
                    }
                }
            }
        """

        variables = {
            "input": {
                "commentId": relay.to_base64(types.Comment, "0"),
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["deleteComment"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "评论不存在")

    def test_update_comment_not_exist(self):
        mutation = """
            mutation updateComment($input: UpdateCommentInput!) {
                updateComment(input: $input) {
                    ... on OperationInfo {
                        __typename
                        messages {
                            message
                        }
                    }
                }
            }
        """
        variables = {
            "input": {
                "id": relay.to_base64(types.Comment, "0"),
                "body": "hello",
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["updateComment"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "评论不存在")


class DifferentUserTopicTests(GraphQLTestCase):
    """测试用户操作其他用户创建的东西"""

    fixtures = ["users", "board", "push_disabled"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="test2")
        self.client.authenticate(self.user)

    def test_delete_topic(self):
        mutation = """
            mutation deleteTopic($input: DeleteTopicInput!) {
                deleteTopic(input: $input) {
                    ... on OperationInfo {
                        __typename
                        messages {
                            message
                        }
                    }
                }
            }
        """

        variables = {
            "input": {
                "topicId": relay.to_base64(types.Topic, "1"),
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["deleteTopic"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "只能删除自己创建的话题")

    def test_update_topic(self):
        mutation = """
            mutation updateTopic($input: UpdateTopicInput!) {
                updateTopic(input: $input) {
                    ... on OperationInfo {
                        __typename
                        messages {
                            message
                        }
                    }
                }
            }
        """
        variables = {
            "input": {
                "id": relay.to_base64(types.Topic, "1"),
                "title": "test",
                "description": "some",
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["updateTopic"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "只能修改自己创建的话题")


class DifferentUserCommentTests(GraphQLTestCase):
    """测试用户操作其他用户创建的东西"""

    fixtures = ["users", "board", "push_disabled"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="test2")
        self.client.authenticate(self.user)

    def test_delete_comment(self):
        mutation = """
            mutation deleteComment($input: DeleteCommentInput!) {
                deleteComment(input: $input) {
                    ... on OperationInfo {
                        __typename
                        messages {
                            message
                        }
                    }
                }
            }
        """

        variables = {
            "input": {
                "commentId": relay.to_base64(types.Comment, "1"),
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["deleteComment"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "只能删除自己创建的评论")

    def test_update_comment(self):
        mutation = """
            mutation updateComment($input: UpdateCommentInput!) {
                updateComment(input: $input) {
                    ... on OperationInfo {
                        __typename
                        messages {
                            message
                        }
                    }
                }
            }
        """
        variables = {
            "input": {
                "id": relay.to_base64(types.Comment, "1"),
                "body": "hello",
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["updateComment"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "只能修改自己创建的评论")


class MarkdownTests(TestCase):
    def test_unmark(self):
        markdown = "# 标题\n\n- 列表一\n- 列表二"

        plaintext = unmark(markdown)

        self.assertEqual(plaintext, "标题\n\n列表一\n列表二")

    def test_unmark_url(self):
        markdown = "# 标题\n\n- 列表一\n- [列表二](https://test.com)"

        plaintext = unmark(markdown)

        self.assertEqual(plaintext, "标题\n\n列表一\n列表二")
