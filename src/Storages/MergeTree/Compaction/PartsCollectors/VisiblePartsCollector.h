#pragma once

#include <Storages/MergeTree/MergeTreeData.h>
#include <Storages/MergeTree/Compaction/PartsCollectors/IPartsCollector.h>

namespace DB
{

class VisiblePartsCollector : public IPartsCollector
{
    MergeTreeData::DataPartsVector collectInitial() const;
    MergeTreeData::DataPartsVector filterByPartitions(MergeTreeData::DataPartsVector && parts, const std::optional<PartitionIdsHint> & partitions_hint) const;
    PartsRanges filterByTxVisibility(
        MergeTreeData::DataPartsVector && parts,
        const StorageMetadataPtr & metadata_snapshot,
        const StoragePolicyPtr & storage_policy,
        const time_t & current_time) const;

public:
    explicit VisiblePartsCollector(const MergeTreeData & data_, const MergeTreeTransactionPtr & tx_);
    ~VisiblePartsCollector() override = default;

    PartsRanges collectPartsToUse(
        const StorageMetadataPtr & metadata_snapshot,
        const StoragePolicyPtr & storage_policy,
        const time_t & current_time,
        const std::optional<PartitionIdsHint> & partitions_hint) const override;

private:
    const MergeTreeData & data;
    const MergeTreeTransactionPtr & tx;
};

}
