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

    let params = {
      limit: 20,
      sort: "remark",
      enable: -1, // -1:All, 0:Enabled, 1:Disabled
      host_id: 0,
      offset: 0,
      q: "",
    };

    const response = await api.request({
      url: "/inbounds/",
      method: "GET",
      params: params,
    });

    return response.data.inbounds;
  },
};
