"""日常选股（绕开 baostock）。

官方 `main.py` 的日常模式第一步会调 `DataEngine.sync_today_bulk()`，
该函数依赖 baostock；一旦 IP 被风控拉黑，整条流程会直接异常退出。
本脚本跳过同步步骤，只做「跑策略 + 推飞书」，数据更新交给
`scripts/backfill_sina.py`（新浪源，可增量跑）。

完整日常流程（baostock 被封时）：

    1) .venv\\Scripts\\python.exe scripts/backfill_sina.py     # 增量补数据
    2) .venv\\Scripts\\python.exe scripts/run_daily.py         # 跑策略 + 推送

参数
----
--no-push    只打印选股结果，不推飞书（本地调试/查看用）
--only       只跑指定策略，逗号分隔，如 --only turtle,ma_volume
             可选标识：ma_volume / turtle / flag / shakeout / limit_down / rps / private
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

from sequoia_x.core.config import get_settings  # noqa: E402
from sequoia_x.core.logger import get_logger  # noqa: E402
from sequoia_x.data.engine import DataEngine  # noqa: E402
from sequoia_x.notify.feishu import FeishuNotifier  # noqa: E402
from sequoia_x.strategy.base import BaseStrategy  # noqa: E402
from sequoia_x.strategy.high_tight_flag import HighTightFlagStrategy  # noqa: E402
from sequoia_x.strategy.limit_up_shakeout import LimitUpShakeoutStrategy  # noqa: E402
from sequoia_x.strategy.ma_volume import MaVolumeStrategy  # noqa: E402
from sequoia_x.strategy.private_placement import PrivatePlacementStrategy  # noqa: E402
from sequoia_x.strategy.rps_breakout import RpsBreakoutStrategy  # noqa: E402
from sequoia_x.strategy.turtle_trade import TurtleTradeStrategy  # noqa: E402
from sequoia_x.strategy.uptrend_limit_down import UptrendLimitDownStrategy  # noqa: E402

# 与 main.py 保持一致的策略装配顺序
STRATEGY_MAP: dict[str, type[BaseStrategy]] = {
    "ma_volume": MaVolumeStrategy,
    "turtle": TurtleTradeStrategy,
    "flag": HighTightFlagStrategy,
    "shakeout": LimitUpShakeoutStrategy,
    "limit_down": UptrendLimitDownStrategy,
    "rps": RpsBreakoutStrategy,
    "private": PrivatePlacementStrategy,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Sequoia-X 日常选股（跳过 baostock 同步）")
    parser.add_argument("--no-push", action="store_true", help="只打印结果，不推飞书")
    parser.add_argument("--only", default="", help="只跑指定策略，逗号分隔标识")
    args = parser.parse_args()

    settings = get_settings()
    logger = get_logger(__name__)
    engine = DataEngine(settings)

    keys = [k.strip() for k in args.only.split(",") if k.strip()] or list(STRATEGY_MAP)
    unknown = [k for k in keys if k not in STRATEGY_MAP]
    if unknown:
        print(f"未知策略标识：{unknown}；可选：{list(STRATEGY_MAP)}")
        return

    notifier = None if args.no_push else FeishuNotifier(settings)

    print(f"库内股票 {len(engine.get_local_symbols())} 只", flush=True)

    for key in keys:
        cls = STRATEGY_MAP[key]
        strategy = cls(engine=engine, settings=settings)
        name = type(strategy).__name__
        try:
            selected = strategy.run()
        except Exception as exc:  # noqa: BLE001
            print(f"{name} 执行失败：{type(exc).__name__} {exc}", flush=True)
            logger.exception(f"{name} 执行失败")
            continue

        print(f"{name}: {len(selected)} 只 -> {selected}", flush=True)

        if selected and notifier:
            notifier.send(
                symbols=selected,
                strategy_name=name,
                webhook_key=strategy.webhook_key,
            )
        elif selected:
            print(f"  （--no-push，未推送）", flush=True)


if __name__ == "__main__":
    main()
