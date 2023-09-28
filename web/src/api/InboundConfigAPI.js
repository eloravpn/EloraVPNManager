import React from "react";
import { api } from "./axios";
import login from "../views/Dashboard/Login";
import { getAuthToken } from "./AuthStorage";
import axios from "axios";

export const InboundConfigAPI = {
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
  create: async function (inboundConfig) {
    await api.request({
      url: `/inbound-configs/`,
      method: "POST",
      data: inboundConfig,
    });
  },
  copy: async function (inboundConfigId) {
    await api.request({
      url: `/inbound-configs/${inboundConfigId}/copy/`,
      method: "POST",
    });
  },
  update: async function (inboundConfig) {
    await api.request({
      url: `/inbound-configs/${inboundConfig.id}`,
      method: "PUT",
      data: inboundConfig,
    });
  },
  delete: async function (inboundConfigId) {
    await api.request({
      url: `/inbound-configs/${inboundConfigId}`,
      method: "DELETE",
    });
  },
  getAll: async function () {

    let params = {
      limit: 20,
      sort: "-sni",
      enable: -1, // -1:All, 0:Enabled, 1:Disabled
      inbound_id: 0,
      offset: 0,
      q: "",
    };

    const response = await api.request({
      url: "/inbound-configs/",
      method: "GET",
      params: params,
    });

    return response.data.inbound_configs;
  },
};
