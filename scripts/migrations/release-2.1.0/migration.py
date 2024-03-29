import asyncio
import argparse
import bittensor as bt
from redis import asyncio as aioredis

from subnet.shared.utils import get_redis_password
from subnet.shared.checks import check_environment

# This migration is to clean useless keys and new ones

def check_redis(args):
    try:
        asyncio.run(check_environment(args.redis_conf_path))
    except AssertionError as e:
        bt.logging.warning(
            f"Something is missing in your environment: {e}. Please check your configuration, use the README for help, and try again."
        )


async def rollout(args):
    try:
        bt.logging.info(
            f"Loading database from {args.database_host}:{args.database_port}"
        )
        redis_password = get_redis_password(args.redis_password)
        database = aioredis.StrictRedis(
            host=args.database_host,
            port=args.database_port,
            db=args.database_index,
            password=redis_password,
        )

        bt.logging.info("Rollout starting")
        async for key in database.scan_iter("*"):
            metadata_dict = await database.hgetall(key)

            # Remove keys
            if b"subtensor_successes" in metadata_dict:
                await database.hdel(key, b"subtensor_successes")
            if b"subtensor_attempts" in metadata_dict:
                await database.hdel(key, b"subtensor_attempts")
            if b"metric_successes" in metadata_dict:
                await database.hdel(key, b"metric_successes")
            if b"metric_attempts" in metadata_dict:
                await database.hdel(key, b"metric_attempts")
            if b"total_successes" in metadata_dict:
                await database.hdel(key, b"total_successes")
            if b"tier" in metadata_dict:
                await database.hdel(key, b"tier")

            # Add keys
            if b"uid" not in metadata_dict:
                await database.hset(key, b"uid", -1)
            if b"version" not in metadata_dict:
                await database.hset(key, b"version", "")
            if b"country" not in metadata_dict:
                await database.hset(key, b"country", "")
            if b"score" not in metadata_dict:
                await database.hset(key, b"score", 0)
            if b"availability_score" not in metadata_dict:
                await database.hset(key, b"availability_score", 0)
            if b"latency_score" not in metadata_dict:
                await database.hset(key, b"latency_score", 0)
            if b"reliability_score" not in metadata_dict:
                await database.hset(key, b"reliability_score", 0)
            if b"distribution_score" not in metadata_dict:
                await database.hset(key, b"distribution_score", 0)
            if b"challenge_successes" not in metadata_dict:
                await database.hset(key, b"challenge_successes", 0)
            if b"challenge_attempts" not in metadata_dict:
                await database.hset(key, b"challenge_attempts", 0)

        bt.logging.info("Rollout done")
    except Exception as e:
        bt.logging.error(f"Error converting to new schema: {e}")


async def rollback(args):
    try:
        bt.logging.info(
            f"Loading database from {args.database_host}:{args.database_port}"
        )
        redis_password = get_redis_password(args.redis_password)
        database = aioredis.StrictRedis(
            host=args.database_host,
            port=args.database_port,
            db=args.database_index,
            password=redis_password,
        )

        bt.logging.info("Rollback starting")
        async for key in database.scan_iter("*"):
            metadata_dict = await database.hgetall(key)

            # Remove keys
            if b"uid" in metadata_dict:
                await database.hdel(key, b"uid")
            if b"version" in metadata_dict:
                await database.hdel(key, b"version")
            if b"country" in metadata_dict:
                await database.hdel(key, b"country")
            if b"score" in metadata_dict:
                await database.hdel(key, b"score")
            if b"availability_score" in metadata_dict:
                await database.hdel(key, b"availability_score")
            if b"latency_score" in metadata_dict:
                await database.hdel(key, b"latency_score")
            if b"reliability_score" in metadata_dict:
                await database.hdel(key, b"reliability_score")
            if b"distribution_score" in metadata_dict:
                await database.hdel(key, b"distribution_score")

            # Add keys
            if b"subtensor_successes" not in metadata_dict:
                await database.hset(key, b"subtensor_successes", 0)
            if b"subtensor_attempts" not in metadata_dict:
                await database.hset(key, b"subtensor_attempts", 0)
            if b"metric_successes" not in metadata_dict:
                await database.hset(key, b"metric_successes", 0)
            if b"metric_attempts" not in metadata_dict:
                await database.hset(key, b"metric_attempts", 0)
            if b"total_successes" not in metadata_dict:
                await database.hset(key, b"total_successes", 0)
            if b"tier" not in metadata_dict:
                await database.hset(key, b"tier", "Bronze")
            if b"challenge_successes" not in metadata_dict:
                await database.hset(key, b"challenge_successes", 0)
            if b"challenge_attempts" not in metadata_dict:
                await database.hset(key, b"challenge_attempts", 0)

        bt.logging.info("Rollback done")
    except Exception as e:
        bt.logging.error(f"Error converting to new schema: {e}")


async def main(args):
    if args.run_type == "rollout":
        await rollout(args)
    else:
        await rollback(args)


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--run-type",
            type=str,
            default="rollout",
            help="Type of migration you want too execute. Possible values are rollout or rollback)",
        )
        parser.add_argument(
            "--redis_password",
            type=str,
            default=None,
            help="password for the redis database",
        )
        parser.add_argument(
            "--redis_conf_path",
            type=str,
            default="/etc/redis/redis.conf",
            help="path to the redis configuration file",
        )
        parser.add_argument("--database_host", type=str, default="localhost")
        parser.add_argument("--database_port", type=int, default=6379)
        parser.add_argument("--database_index", type=int, default=1)
        args = parser.parse_args()

        asyncio.run(main(args))
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    except ValueError as e:
        print(f"ValueError: {e}")
