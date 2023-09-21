import React, { useEffect, useState } from "react";
import { UserAPI } from "../../../../api/UserAPI";
import { Avatar, Tag, TagLabel } from "@chakra-ui/react";

const User = ({ userId, fullName }) => {
  const [user, setUser] = useState();
  const [telegramLink, setTelegramLink] = useState();

  return (
    <Tag size="sm" colorScheme="red" borderRadius="full">
      <a target="_blank" href={telegramLink}>
        <TagLabel>{fullName ? fullName : ""}</TagLabel>
      </a>
    </Tag>
  );
};

export default User;
