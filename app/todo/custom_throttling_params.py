from rest_framework.throttling import UserRateThrottle


class FloodRateThrottle(UserRateThrottle):
    scope = 'flood'


class BurstRateThrottle(UserRateThrottle):
    scope = 'burst'


class SustainedRateThrottle(UserRateThrottle):
    scope = 'sustained'


class NormalRateThrottle(UserRateThrottle):
    scope = 'normal'
