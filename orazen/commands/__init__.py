# flake8: noqa: F401
"""
Commands module.
Contains all start-commands, subcommands and CLI Interface creation.

Note: Be careful with file-scoped imports in these subfiles.
    as they are parsed on startup, nothing containing optional modules should be loaded.
"""

from orazen.commands.analyze_commands import start_analysis_entries_exits
from orazen.commands.arguments import Arguments
from orazen.commands.build_config_commands import start_new_config, start_show_config
from orazen.commands.data_commands import (
    start_convert_data,
    start_convert_trades,
    start_download_data,
    start_list_data,
    start_list_trades_data,
)
from orazen.commands.db_commands import start_convert_db
from orazen.commands.deploy_commands import (
    start_create_userdir,
    start_install_ui,
    start_new_strategy,
)
from orazen.commands.hyperopt_commands import start_hyperopt_list, start_hyperopt_show
from orazen.commands.list_commands import (
    start_list_exchanges,
    start_list_freqAI_models,
    start_list_hyperopt_loss_functions,
    start_list_markets,
    start_list_strategies,
    start_list_timeframes,
    start_show_trades,
)
from orazen.commands.optimize_commands import (
    start_backtesting,
    start_backtesting_show,
    start_edge,
    start_hyperopt,
    start_lookahead_analysis,
    start_recursive_analysis,
)
from orazen.commands.pairlist_commands import start_test_pairlist
from orazen.commands.plot_commands import start_plot_dataframe, start_plot_profit
from orazen.commands.strategy_utils_commands import start_strategy_update
from orazen.commands.trade_commands import start_trading
from orazen.commands.webserver_commands import start_webserver
