import React, { useEffect, useState } from "react";
import { AccountAPI } from "../../../../api/AccountAPI";
import { Stat, StatLabel, Text } from "@chakra-ui/react";
import { ArrowDownIcon, ArrowUpIcon, UpDownIcon } from "@chakra-ui/icons";

export const AccountUsageStat = ({ accountId, stateName, delta }) => {
  const units = [
    "bytes",
    "KiB",
    "MiB",
    "GiB",
    "TiB",
    "PiB",
    "EiB",
    "ZiB",
    "YiB",
  ];

  function niceBytes(x) {
    let l = 0,
      n = parseInt(x, 10) || 0;

    while (n >= 1024 && ++l) {
      n = n / 1024;
    }

    return n.toFixed(n < 10 && l > 0 ? 1 : 0) + " " + units[l];
  }

  const [download, setDownload] = useState(0);
  const [upload, setUpload] = useState(0);
  useEffect(() => {
    if (accountId) {
      AccountAPI.getAccountUsedTraffic(accountId, delta ? delta : 1).then(
        (res) => {
          setUpload(res["upload"]);
          setDownload(res["download"]);
        }
      );
    } else if (accountId === 0) {
      AccountAPI.getAllAccountUsedTraffic(delta ? delta : 1).then((res) => {
        setUpload(res["upload"]);
        setDownload(res["download"]);
      });
    }
  }, [accountId]);

  return (
    <div>
      <Stat size={"sm"}>
        <StatLabel>{stateName ? stateName : ""}</StatLabel>
        <Text fontSize="md" title="Upload">
          {/* <StatArrow type="increase" /> */}
          <ArrowUpIcon boxSize={5} />
          {upload ? niceBytes(upload) : 0}
        </Text>
        <Text fontSize="md" title="Download">
          {/* <StatArrow type="decrease" /> */}
          <ArrowDownIcon boxSize={5} />
          {download ? niceBytes(download) : 0}
        </Text>

        <Text fontSize="lg" title="Total">
          {/* <StatArrow type="decrease" /> */}
          <UpDownIcon boxSize={5} />
          {niceBytes(upload + download)}
        </Text>
        {/* <StatHelpText>23.36%</StatHelpText> */}
      </Stat>
    </div>
  );
};
