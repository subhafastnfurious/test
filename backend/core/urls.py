from rest_framework import routers

from core.views import OfficeSpaceViewSet

router = routers.SimpleRouter()
router.register('office-spaces', OfficeSpaceViewSet, base_name='office-spaces')
urlpatterns = router.urls