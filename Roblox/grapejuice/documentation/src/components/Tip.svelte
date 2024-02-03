<script lang="ts">
    import StarlightIcon from "./StarlightIcon.svelte";
    type TipType = "danger" | "info" | "warning";

    export let type: TipType = "info";
    export let title: string | null = null;
    export let icon: string | null = null;
</script>

{#if type === "info"}
    <div class="flex flex-col bg-blue-600 text-white p-3 border border-blue-950 rounded-xl">
        <span class="flex flex-row items-center gap-2 pb-2">
            <StarlightIcon name={icon || "star"} />
            <span class="font-bold">{title || "Tip"}</span>
        </span>
        <span><slot /></span>
    </div>
{:else if type === "danger"}
    <div class="flex flex-col bg-red-600 text-white font-bold p-3 border border-red-900 rounded-xl">
        <span class="flex flex-row items-center gap-2 pb-2">
            <StarlightIcon name={icon || "error"} />
            <span class="font-bold">{title || "Watch out!"}</span>
        </span>
        <span><slot /></span>
    </div>
{:else if type === "warning"}
    <div class="flex flex-col bg-yellow-600 text-white font-bold p-3 border border-red-900 rounded-xl">
        <span class="flex flex-row items-center gap-2 pb-2">
            <StarlightIcon name={icon || "error"} />
            <span class="font-bold">{title || "Watch out!"}</span>
        </span>
        <span><slot /></span>
    </div>
{:else}
    Invalid Tip Type :(
{/if}
