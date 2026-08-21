# flake8: noqa: F401
# isort: off
from orazen.resolvers.iresolver import IResolver
from orazen.resolvers.exchange_resolver import ExchangeResolver

# isort: on
# Don't import HyperoptResolver to avoid loading the whole Optimize tree
# from orazen.resolvers.hyperopt_resolver import HyperOptResolver
from orazen.resolvers.pairlist_resolver import PairListResolver
from orazen.resolvers.protection_resolver import ProtectionResolver
from orazen.resolvers.strategy_resolver import StrategyResolver
