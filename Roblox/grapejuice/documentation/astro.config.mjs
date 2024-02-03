import starlight from "@astrojs/starlight";
import { defineConfig } from "astro/config";

import svelte from "@astrojs/svelte";
import tailwind from "@astrojs/tailwind";

// https://astro.build/config
export default defineConfig({
    site: "https://brinkervii.gitlab.io/grapejuice/",
    base: "/grapejuice",
    output: "static",
    integrations: [
        starlight({
            title: "Grapejuice",
            logo: {
                src: "./src/assets/images/grapejuice.svg",
            },
            social: {
                gitlab: "https://gitlab.com/brinkervii/grapejuice",
                discord: "https://discord.gg/S9QrDxJdDW",
            },
            customCss: ["./src/tailwind.css"],
            sidebar: [
                {
                    label: "Start Here",
                    items: [
                        {
                            label: "Getting started with Grapejuice",
                            link: "/start-here",
                        },
                    ],
                },
                {
                    label: "Install on...",
                    items: [
                        {
                            label: "Ubuntu",
                            link: "/install-on/ubuntu",
                        },
                        {
                            label: "Linux Mint",
                            link: "/install-on/linux-mint",
                        },
                        {
                            label: "Pop! OS by System76",
                            link: "/install-on/pop",
                        },
                        {
                            label: "Debian",
                            link: "/install-on/debian",
                        },
                        {
                            label: "Fedora Workstation",
                            link: "/install-on/fedora",
                        },
                        {
                            label: "Steam OS",
                            link: "/install-on/steam-os",
                        },
                        {
                            label: "Arch Linux",
                            link: "/install-on/arch",
                        },
                        {
                            label: "Manjaro",
                            link: "/install-on/manjaro",
                        },
                        {
                            label: "OpenSUSE",
                            link: "/install-on/opensuse",
                        },
                        {
                            label: "Flatpak",
                            link: "/install-on/flatpak",
                        },
                        {
                            label: "Solus",
                            link: "/install-on/solus",
                        },
                        {
                            label: "Void Linux",
                            link: "/install-on/void",
                        },
                        {
                            label: "Slackware",
                            link: "/install-on/slackware",
                        },
                        {
                            label: "FreeBSD",
                            link: "/install-on/freebsd",
                        },
                    ],
                },
                {
                    label: "Guides",
                    items: [
                        {
                            label: "Custom Wine Builds",
                            link: "/guides/using-custom-wine-builds",
                        },
                    ],
                },
                {
                    label: "Reference",
                    autogenerate: {
                        directory: "reference",
                    },
                },
            ],
        }),
        tailwind({
            applyBaseStyles: false,
        }),
        svelte(),
    ],
});
