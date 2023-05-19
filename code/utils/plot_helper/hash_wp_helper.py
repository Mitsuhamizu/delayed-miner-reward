import collections
from datetime import datetime
from difflib import SequenceMatcher

import numpy as np
import pandas as pd


def get_closest_shares(mapped_pool_name, timestamp, pool_shares):
    # timestamp_in_datetime = datetime.fromtimestamp(row["winner_timestamp"])
    timestamp_in_datetime = datetime.fromtimestamp(timestamp)
    i = np.argmin(np.abs(pool_shares.index.to_pydatetime() - timestamp_in_datetime))

    # return pool_shares.iloc[i][names_mapping[row["winner_id"]]]
    return pool_shares.iloc[i][mapped_pool_name]


def get_hashrate_wp_relation(data, x_range, ideal_relation):
    hashrate_label = "Pool shares"
    case_label = "cases"
    wp_label = "Probability of Main Chain Inclusion"
    headstart_label = "headstart"
    chain_label = "chain"
    gammas = [0.5, 0.4, 0.3]

    result = pd.DataFrame(
        columns=[
            hashrate_label,
            case_label,
            wp_label,
            headstart_label,
            chain_label,
        ]
    )
    hashrate_for_ideal = {}
    # init a empty dataframe, each element is a list.
    for x_start in x_range:
        hashrate_for_ideal[x_start] = []
        result.loc[result.shape[0]] = [x_start, [], 0.5, [], "BTC"]
        result.loc[result.shape[0]] = [x_start, [], 0.5, [], "ETH"]

    for index, row in data.iterrows():

        x_interval_begin = x_range[x_range <= row["hashrate"]].max()

        # get the max hashrate_begin below the target value, and get the index in result.
        hashrate_for_ideal[x_interval_begin].append(row["hashrate"])

        satisfied_index = result.index[
            (result[hashrate_label] == x_interval_begin)
            & (result[chain_label] == row[chain_label])
        ].tolist()[0]

        result.at[satisfied_index, case_label] += [row["role"]]
        result.at[satisfied_index, headstart_label].append(row["headstart"])

    # convert cases to ratio.
    for index, row in result.iterrows():

        if row[chain_label] in ["ETH", "BTC"]:
            if row["cases"] != []:
                result.at[index, wp_label] = round(
                    sum([iter == "winner" for iter in row[case_label]])
                    / len(row[case_label]),
                    2,
                )
            else:
                result.at[index, wp_label] = None
                print("Missing data.")
    # get the ideal data.
    for hashrate, list in hashrate_for_ideal.items():
        for gamma_iter in gammas:
            result.loc[result.shape[0]] = [
                hashrate,
                [],
                ideal_relation(hashrate + 0.025, gamma_iter),
                0,
                "γ = {}".format(gamma_iter),
            ]
    return result


def get_hashrate_interval(x_begin, x_end, x_interval):
    x_range = np.linspace(x_begin, x_end, int((x_end - x_begin) / x_interval + 1))
    x_range = np.array([round(iter, 3) for iter in x_range])

    return x_range


def add_hashrate_and_headstart(forks, names_in_share, filter_range, pool_shares):
    data = pd.DataFrame(columns=["hashrate", "headstart", "role"])
    total_blocks, blocks_within_interval, block_with_known_hash = 0, 0, 0
    shares = []
    for index, row in forks.iterrows():
        # one row, two blocks.
        total_blocks += 2
        for role in ["winner", "loser"]:
            if row[role + "_id"] in names_in_share:
                block_with_known_hash += 1
                if role == "winner":
                    headstart = -row["diff"] / 1000
                elif role == "loser":
                    headstart = row["diff"] / 1000
                share = get_closest_shares(
                    row[role + "_id"],
                    row[role + "_timestamp"] / 1000,
                    pool_shares,
                )
                shares.append(share)
                if headstart < filter_range + 10 and headstart > -filter_range:
                    blocks_within_interval += 1
                    data.loc[data.shape[0]] = [float(share), headstart, role]
    print(
        "total blocks: {}\nblocks with known rate: {}\nblocks within the interval: {}".format(
            total_blocks, block_with_known_hash, blocks_within_interval
        )
    )
    return data


def get_uncle_height_with_known_hashrate(forks, names_in_share):
    fork_height = list(forks["fork_height"])
    fork_height_count = collections.Counter(fork_height)
    height_with_two_uncle = [
        index for index, count in fork_height_count.items() if count > 1
    ]

    uncle_block_with_brother_and_known_hashrate = 0
    uncle_block_with_known_hashrate = 0
    for index, row in forks.iterrows():
        # one row, two blocks.
        for role in ["winner", "loser"]:
            if row[role + "_id"] in names_in_share:
                uncle_block_with_known_hashrate += 1
                if row["fork_height"] in height_with_two_uncle:
                    uncle_block_with_brother_and_known_hashrate += 1

    return uncle_block_with_known_hashrate, uncle_block_with_brother_and_known_hashrate


def convert_name_to_share_version(forks, names_in_share, chain):
    roles = ["winner_id", "loser_id", "next_block_id"]
    name_checked = set()
    name_map = dict()
    count = 0
    for index, row in forks.iterrows():
        count += 1
        for id_in_forks in roles:
            if row[id_in_forks] not in name_checked:
                for name_in_share_iter in names_in_share:
                    current_similarity = SequenceMatcher(
                        None, name_in_share_iter, row[id_in_forks]
                    ).ratio()
                    if current_similarity >= 0.5:
                        if row[id_in_forks] in name_map.keys():
                            old_similarity = SequenceMatcher(
                                None, row[id_in_forks], name_map[row[id_in_forks]]
                            ).ratio()

                            new_similarity = current_similarity
                            if new_similarity > old_similarity:
                                name_map[row[id_in_forks]] = name_in_share_iter
                        else:
                            name_map[row[id_in_forks]] = name_in_share_iter
                        name_checked.add(id_in_forks)

    if chain == "BTC":
        del name_map["BTC.com"]
        del name_map["KanoPool"]
    elif chain == "ETH":
        name_to_deleted = [
            "KuCoin Pool",
            "Poolin 2",
            "GPUMINE Pool 1",
            "Binance Pool",
            "Poolin 3",
            "SBI Crypto Pool",
            "Poolin 4",
            "Crazy Pool",
            "SoloPool.org",
            "666 Mining Pool",
            "Minerall Pool",
            "HeroMiners",
            "Cruxpool",
            "WoolyPooly",
            "Pool2Mine 1",
            "AntPool 2",
            "OKEX Mining Pool 1",
            "Comining 1",
            "Firebird Mining Pool 1",
            "Huobi Mining Pool 2",
            "xnpool",
            "C3Pool",
            "firepool",
            "EthashPool 2",
            "Easy2Mine",
            "Bw Pool",
            "ICanMining.ru",
            "Baypool",
            "Uleypool",
            "Huobi Mining Pool",
            "PandaMiner",
            "DigiPools 2",
            "Poolin",
            "HashON Pool",
            "MATPool",
            "FKPool",
            "WaterholePool",
            "SaturnPool",
            "DigiPools",
            "DwarfPool",
            "AntPool",
            "EthashPool 1",
            "Huixingpool.com",
            "NoobPool",
            "EtherDig",
            "xnpool.cn",
            "BitClubPool",
            "KuveraPool",
            "PoolHub",
            "PandaPool",
            "TwethPool",
            "etherTrench",
            "MinerGate",
            "CryptoPool",
            "poolgpu",
        ]
        for name_to_deleted_iter in name_to_deleted:
            if name_to_deleted_iter in name_map.keys():
                del name_map[name_to_deleted_iter]

    for org_name, new_name in name_map.items():
        for id_in_forks in roles:
            forks[id_in_forks] = forks[id_in_forks].replace(org_name, new_name)

    return forks


def get_data_with_hashrate(forks, pool_shares, headstart_bound, chain):
    names_in_share = pool_shares.columns.values
    forks = convert_name_to_share_version(forks, names_in_share, chain)

    pool_shares.index = pd.to_datetime(pool_shares.index)

    data = add_hashrate_and_headstart(
        forks, names_in_share, headstart_bound, pool_shares
    )
    data["chain"] = chain
    return data
