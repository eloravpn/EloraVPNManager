import React from "react";
import { api } from "./axios";
import login from "../views/Dashboard/Login";
import { getAuthToken } from "./AuthStorage";
import axios from "axios";

export const InboundAPI = {
  // get: async function (hostId) {
  //
  //     const response = await api.request({
  //         url: `/hosts/${hostId}`,
  //         method: "GET",
  //     })
  //
  //     // returning the product returned by the API
  //     return response.data;
  // },
  create: async function (inbound) {
    await api.request({
      url: `/inbounds/`,
      method: "POST",
      data: inbound,
    });
  },
  update: async function (inbound) {
    await api.request({
      url: `/inbounds/${inbound.id}`,
      method: "PUT",
      data: inbound,
    });
  },
  delete: async function (inboundId) {
    await api.request({
      url: `/inbounds/${inboundId}`,
      method: "DELETE",
    });
  },
  getAll: async function () {
    const response = await api.request({
      url: "/inbounds/",
      method: "GET",
    });

    return response.data.inbounds;
  },
};
