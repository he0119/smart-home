import graphene
from graphene_django.types import DjangoObjectType
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from .models import AutowateringData, Device


#region query
class DeviceType(DjangoObjectType):
    class Meta:
        model = Device
        fields = '__all__'


class AutowateringDataType(DjangoObjectType):
    class Meta:
        model = AutowateringData
        fields = '__all__'


class Query(graphene.ObjectType):
    device = graphene.Field(DeviceType, id=graphene.ID(required=True))
    devices = graphene.List(
        DeviceType,
        number=graphene.Int(),
    )
    device_data = graphene.List(
        AutowateringDataType,
        device_id=graphene.ID(),
        number=graphene.Int(),
    )

    @login_required
    def resolve_device(self, info, id):
        return Device.objects.get(pk=id)

    @login_required
    def resolve_devices(self, info, **kwargs):
        number = kwargs.get('number')

        q = Device.objects.all()
        if number:
            return q[:number]
        return q

    @login_required
    def resolve_device_data(self, info, **kwargs):
        device_id = kwargs.get('device_id')
        number = kwargs.get('number')

        # 时间排序，最新的在最上面
        q = AutowateringData.objects.all().order_by('-id')
        if device_id:
            q = q.filter(device__id=device_id)
        if number:
            q = q[:number]

        return q


# endregion


#region mutation
#region inputs
class AddDeviceInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    device_type = graphene.String(required=True)
    location = graphene.String()


class UpdateDeviceInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    name = graphene.String()
    device_type = graphene.String()
    location = graphene.String()


class DeleteDeviceInput(graphene.InputObjectType):
    device_id = graphene.ID(required=True, description='设备的 ID')


#endregion


class AddDeviceMutation(graphene.Mutation):
    class Arguments:
        input = AddDeviceInput(required=True)

    device = graphene.Field(DeviceType)

    @login_required
    def mutate(self, info, **kwargs):
        input = kwargs.get('input')

        device = Device(
            name=input.title,
            device_type=input.device_type,
            location=input.location,
            is_online=False,
        )
        device.save()
        return AddDeviceMutation(device=device)


class DeleteDeviceMutation(graphene.Mutation):
    class Arguments:
        input = DeleteDeviceInput(required=True)

    deletedId = graphene.ID()

    @login_required
    def mutate(self, info, **kwargs):
        input = kwargs.get('input')

        try:
            device = Device.objects.get(pk=input.device_id)
            device.delete()
            return DeleteDeviceMutation(deletedId=input.device_id)
        except Device.DoesNotExist:
            raise GraphQLError('设备不存在')


class UpdateDeviceMutation(graphene.Mutation):
    class Arguments:
        input = UpdateDeviceInput(required=True)

    device = graphene.Field(DeviceType)

    @login_required
    def mutate(self, info, **kwargs):
        input = kwargs.get('input')

        try:
            device = Device.objects.get(pk=input.id)
        except Device.DoesNotExist:
            raise GraphQLError('设备不存在')

        # 仅在传入数据时修改
        if input.name is not None:
            device.name = input.name
        if input.device_type is not None:
            device.device_type = input.device_type
        if input.location is not None:
            device.location = input.location
        device.save()
        return UpdateDeviceMutation(device=device)


class Mutation(graphene.ObjectType):
    add_device = AddDeviceMutation.Field()
    delete_device = DeleteDeviceMutation.Field()
    update_device = UpdateDeviceMutation.Field()


#endregion
