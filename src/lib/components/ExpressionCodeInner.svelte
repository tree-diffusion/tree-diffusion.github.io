<script>
	export let data;
	export let depth = 0;

	const literalLookup = {
		one: 1,
		two: 2,
		three: 3,
		four: 4,
		five: 5,
		six: 6,
		seven: 7,
		eight: 8,
		nine: 9,
		zero: 0,
		ten: 10,
		eleven: 11,
		twelve: 12,
		thirteen: 13,
		fourteen: 14,
		fifteen: 15,
		zerodeg: 0,
		onedeg: 45,
		twodeg: 90,
		threedeg: 135,
		fourdeg: 180,
		fivedeg: 225,
		sixdeg: 270,
		sevendeg: 315
	};

	const circleString = () => {
		const r = data.children[0].data;
		const x = data.children[1].data;
		const y = data.children[2].data;

		return `r=${literalLookup[r]} x=${literalLookup[x]} y=${literalLookup[y]}`;
	};

	const quadString = () => {
		const x = data.children[0].data;
		const y = data.children[1].data;
		const w = data.children[2].data;
		const h = data.children[3].data;
		const angle = data.children[4].data;

		return `x=${literalLookup[x]} y=${literalLookup[y]} w=${literalLookup[w]} h=${literalLookup[h]} angle=${literalLookup[angle]}°`;
	};
</script>

<!-- <div>
	{#if data}
		<div>{data.data}</div>
		{#each data.children as child}
			<span style:width></span>
			<svelte:self data={child} depth={depth + 1}></svelte:self>
		{/each}
	{/if}
</div> -->

{#if data}
	{#if data.data === 's'}
		<svelte:self data={data.children[0]} {depth}></svelte:self>
	{:else if data.data === 'binop'}
		<div>
			(<span class="text-blue-700 font-bold"
				>{data.children[0].data === 'subtract' ? 'Subtract' : 'Add'}</span
			>
		</div>
		<div class="flex">
			<div>&nbsp;&nbsp;</div>
			<div>
				<div>
					<svelte:self data={data.children[1]} depth={depth + 1}></svelte:self>
				</div>
				<div>
					<svelte:self data={data.children[2]} depth={depth + 1}></svelte:self>
				</div>
			</div>
		</div>
		<div>)</div>
	{:else if data.data === 'circle'}
		<div>
			(<span class="text-blue-700 font-bold">Circle</span>
			{circleString()})
		</div>
	{:else if data.data === 'quad'}
		<div>
			(<span class="text-blue-700 font-bold">Quad</span>
			{quadString()})
		</div>
	{/if}
{/if}
