import graphene
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required

from home.iot.mutations import (AddDeviceMutation, DeleteDeviceMutation,
                                SetDeviceMutation, UpdateDeviceMutation)

from .models import AutowateringData, Device
from .types import (AutowateringDataFilter, AutowateringDataType, DeviceFilter,
                    DeviceType)


class Query(graphene.ObjectType):
    devices = DjangoFilterConnectionField(DeviceType,
                                          filterset_class=DeviceFilter)
    autowatering_data = DjangoFilterConnectionField(
        AutowateringDataType, filterset_class=AutowateringDataFilter)

    @login_required
    def resolve_devices(self, info, **args):
        return Device.objects.all()

    @login_required
    def resolve_autowatering_data(self, info, **args):
        return AutowateringData.objects.all()

class Mutation(graphene.ObjectType):
    add_device = AddDeviceMutation.Field()
    delete_device = DeleteDeviceMutation.Field()
    update_device = UpdateDeviceMutation.Field()
    set_device = SetDeviceMutation.Field()
