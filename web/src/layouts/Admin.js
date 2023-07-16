import React, { useState } from 'react';
import { ChakraProvider, Portal } from "@chakra-ui/react";
// Custom Chakra theme
import theme from 'theme/theme.js';
import Sidebar from "components/Sidebar";
import { HomeIcon } from "../components/Icons/Icons";

import routes from 'routes.js';
import { BrowserRouter, Navigate, Outlet, Route, Routes } from "react-router-dom";
import MainPanel from "../components/Layout/MainPanel";
import PanelContent from "../components/Layout/PanelContent";
import PanelContainer from "../components/Layout/PanelContainer";
import SidebarResponsive from 'components/Sidebar/SidebarResponsive';



const Admin = (props) => {
	const { ...rest } = props;


	const [sidebarVariant, setSidebarVariant] = useState('transparent');
	return (
		<ChakraProvider theme={theme} resetCss={false}>
			<SidebarResponsive
				logoText={props.logoText}
				secondary={props.secondary}
				routes={routes}
				// logo={logo}
				{...rest}
			/>
			<Sidebar
				routes={routes}
				logoText={'PURITY UI DASHBOARD'}
				sidebarVariant={sidebarVariant}
				{...rest}
			/>
			<MainPanel
				w={{
					base: '100%',
					xl: 'calc(100% - 275px)'
				}}>

				<Portal>
				</Portal>
				<PanelContent>
					<PanelContainer>
						<Outlet />
					</PanelContainer>
				</PanelContent>
			</MainPanel>




		</ChakraProvider>
	);
};

export default Admin;