import React, { useEffect, useState } from "react";
import { UserAPI } from "../../../../api/UserAPI";
import { Avatar, Tag, TagLabel } from "@chakra-ui/react";

const User = ({ userId }) => {
  const [user, setUser] = useState();
  const [fullName, setFullName] = useState();
  const [telegramLink, setTelegramLink] = useState();
  useEffect(() => {
    UserAPI.get(userId).then((res) => {
      setUser(res);
      let fullName = res.first_name ? res.first_name : "";

      fullName = fullName + " " + (res.last_name ? res.last_name : "");
      setFullName(fullName);

      if (res.telegram_username)
        setTelegramLink(`https://t.me/${res.telegram_username}`);
      else if (res.telegram_chat_id)
        setTelegramLink(`tg://user?id=${res.telegram_chat_id}`);
    });

    // return (cleanup = () => {});
  }, [userId]);
  return (
    <Tag size="sm" colorScheme="red" borderRadius="full">
      {/* <Avatar size="xs" name={fullName ? fullName : ""} ml={-1} mr={2} /> */}
      <a target="_blank" href={telegramLink}>
        <TagLabel>{fullName ? fullName : ""}</TagLabel>
      </a>
    </Tag>
  );
};

export default User;
