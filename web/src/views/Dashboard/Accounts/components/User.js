import React, { useEffect, useState } from "react";
import { UserAPI } from "../../../../api/UserAPI";

const User = ({ userId }) => {
  const [user, setUser] = useState();
  useEffect(() => {
    UserAPI.get(userId).then((res) => {
      setUser(res);
    });

    // return (cleanup = () => {});
  }, [userId]);
  return <div>{user ? user.first_name : ""}</div>;
};

export default User;
