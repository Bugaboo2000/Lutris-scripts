<script lang="ts">
    import { Icons } from "./StarlightIcons";

    export let name: keyof typeof Icons = "star";
    export let color = "currentColor";
    export let size = "1.5em";
    $: icon = Icons[name] as string;
</script>

<svg viewBox="0 0 24 24" width={size} height={size} fill={color}>
    {@html icon}
</svg>
