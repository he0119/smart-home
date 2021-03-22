from django_filters import FilterSet, OrderingFilter
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required

from .models import AutowateringData, Device


class AutowateringDataFilter(FilterSet):
    class Meta:
        model = AutowateringData
        fields = {
            'device': ['exact'],
            'time': ['exact', 'lt', 'gt'],
        }

    order_by = OrderingFilter(fields=(('time', 'time'), ))


class DeviceFilter(FilterSet):
    class Meta:
        model = Device
        fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'device_type': ['exact', 'icontains', 'istartswith'],
            'location': ['exact', 'icontains', 'istartswith'],
        }

    order_by = OrderingFilter(fields=(
        ('created_at', 'created_at'),
        ('edited_at', 'edited_at'),
        ('is_online', 'is_online'),
        ('online_at', 'online_at'),
        ('offline_at', 'offline_at'),
    ))


class AutowateringDataType(DjangoObjectType):
    class Meta:
        model = AutowateringData
        fields = '__all__'
        interfaces = (relay.Node, )

    @classmethod
    @login_required
    def get_node(cls, info, id):
        return AutowateringData.objects.get(pk=id)


class DeviceType(DjangoObjectType):
    class Meta:
        model = Device
        fields = '__all__'
        interfaces = (relay.Node, )

    autowatering_data = DjangoFilterConnectionField(
        AutowateringDataType, filterset_class=AutowateringDataFilter)

    @login_required
    def resolve_autowatering_data(self, info, **args):
        return self.data

    @classmethod
    @login_required
    def get_node(cls, info, id):
        return Device.objects.get(pk=id)
