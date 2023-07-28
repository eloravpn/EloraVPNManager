import {
  Box,
  Center,
  SimpleGrid,
  Stat,
  StatArrow,
  StatHelpText,
  StatLabel,
  StatNumber,
  StatUpArrow,
} from "@chakra-ui/react";
import React from "react";
import { AccountUsageStat } from "../Users/components/AccountUsageStat";

const Dashboard = () => {
  return (
    <SimpleGrid columns={{ lg: 4, md: 4, sm: 1 }} spacing={10}>
      <Box height="80px" textAlign={"Center"}>
        <AccountUsageStat accountId={0} stateName={"Last Day"} delta={1} />
      </Box>
      <Box height="80px" textAlign={"Center"}>
        <AccountUsageStat accountId={0} stateName={"Last 3 Days"} delta={3} />
      </Box>
      <Box height="80px" textAlign={"Center"}>
        <AccountUsageStat accountId={0} stateName={"Last week"} delta={7} />
      </Box>

      <Box height="80px" textAlign={"Center"}>
        <AccountUsageStat accountId={0} stateName={"Last mounth"} delta={30} />
      </Box>
    </SimpleGrid>
  );
};

export default Dashboard;
