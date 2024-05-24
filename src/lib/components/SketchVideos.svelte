<script>
	let heroVideos = [
		{ video: '/videos/sketch4.mp4', title: 'Sketch 4', thumbnail: '/videos/sketch4.png' },
		{ video: '/videos/sketch1.mp4', title: 'Sketch 1', thumbnail: '/videos/sketch1.png' },
		{ video: '/videos/sketch5.mp4', title: 'Sketch 5', thumbnail: '/videos/sketch5.png' },
		{ video: '/videos/sketch3.mp4', title: 'Sketch 3', thumbnail: '/videos/sketch3.png' },
		{ video: '/videos/sketch2.mp4', title: 'Sketch 2', thumbnail: '/videos/sketch2.png' }
	];

	let currentVideo = heroVideos[0];
</script>

<div class="border-2 border-gray-300 border-solid inline-block p-8 rounded-md">
	<video src={currentVideo.video} autoplay loop muted class="max-w-xl w-full"></video>
</div>
<div class="mt-4 italic">(Select A Sketch Below)</div>
<div class="md:flex md:flex-row md:justify-center md:items-center mt-2">
	{#each heroVideos as video}
		<button
			class="transition border-2 border-solid w-24 h-24 p-2 rounded-md m-2 cursor-pointer"
			class:border-gray-300={currentVideo !== video}
			class:hover:border-gray-500={currentVideo !== video}
			class:border-blue-500={currentVideo === video}
			class:hover:border-blue-500={currentVideo === video}
			class:nice-shadow={currentVideo === video}
			on:click={() => (currentVideo = video)}
		>
			<img src={video.thumbnail} alt={video.thumbnail} class="w-full h-full" />
		</button>
	{/each}
</div>
