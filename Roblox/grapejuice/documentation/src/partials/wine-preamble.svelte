<script lang="ts">
    import Tip from "../components/Tip.svelte";

    export let distroId = "unknown";
    export let distroName = distroId;

    const debianLike = ["Debian", "Ubuntu", "Mint", "Linux Mint"];
    const archLike = ["Arch", "Arch Linux", "Manjaro", "Manjaro Linux"];
    const fedoraLike = ["Fedora"];
</script>

{#if debianLike.includes(distroId) || fedoraLike.includes(distroId)}
    <p class="mb-2">
        Before you do anything with Grapejuice, you need to have Wine installed. Roblox will only work if you have wine-staging 8.0 or higher installed on your system. If your distribution does not have the required Wine version, its recommended to install Wine Staging from the official WineHQ
        website. if you do not want to install another version of Wine globally, you can check out the guide on using custom Wine builds.
    </p>
    <a href="https://wiki.winehq.org/{distroId}" target="_blank">WineHQ download page for {distroName}</a>
{:else if archLike.includes(distroId)}
    <p class="mb-2">
        Before you do anything with Grapejuice, you need to have Wine installed. Roblox will only work if you have wine-staging 8.0 or higher installed on your system.
        You are using {distroName}, which means that you are on the bleeding edge! The {distroName} software repository contains a version of Wine that works with Roblox.
        It is recommended that you install wine-staging from the {distroName} repository.
    </p>
{:else}
    <Tip type="danger" title="Documentation Error">The documentation maintainer entered an incorrect distribution Id, so you are seeing this error now :)</Tip>
{/if}
