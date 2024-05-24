<script>
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	export let color = 'black';
</script>

<button class={'big-button select-none font-sans ' + color + ' ' + $$props.class} on:click>
	<div class="button-grid-wrapper">
		<div class="button-slot-wrapper">
			<slot></slot>
		</div>
		<!-- <div class="big-button-wrapper" :class="{ 'button-show': loading }">
        <Spinner theme="light"></Spinner>
      </div> -->
	</div>
</button>

<style>
	@property --rotate {
		syntax: '<angle>';
		initial-value: 132deg;
		inherits: false;
	}

	.card {
		--borderWidth: 3px;
		background: #1d1f20;
		position: relative;
		border-radius: 10px;
	}

	.card::before {
		content: '';
		width: 104%;
		height: 102%;
		border-radius: 8px;
		background-image: linear-gradient(var(--rotate), #5ddcff, #3c67e3 43%, #4e00c2);
		position: absolute;
		z-index: -1;
		top: -1%;
		left: -2%;
		animation: spin 2.5s linear infinite;
	}

	.card::after {
		position: absolute;
		content: '';
		top: calc(var(--card-height) / 6);
		left: 0;
		right: 0;
		z-index: -1;
		height: 100%;
		width: 100%;
		margin: 0 auto;
		transform: scale(0.8);
		filter: blur(calc(var(--card-height) / 6));
		background-image: linear-gradient(var(--rotate), #5ddcff, #3c67e3 43%, #4e00c2);
		opacity: 1;
		transition: opacity 0.5s;
		animation: spin 2.5s linear infinite;
	}

	@keyframes spin {
		0% {
			--rotate: 0deg;
		}
		100% {
			--rotate: 360deg;
		}
	}

	.gradient-border {
		--borderWidth: 3px;
		background: #1d1f20;
		position: relative;
		border-radius: 10px;
	}
	.gradient-border:after {
		content: '';
		position: absolute;
		top: calc(-1 * var(--borderWidth));
		left: calc(-1 * var(--borderWidth));
		height: calc(100% + var(--borderWidth) * 2);
		width: calc(100% + var(--borderWidth) * 2);
		background: linear-gradient(
			60deg,
			#f79533,
			#f37055,
			#ef4e7b,
			#a166ab,
			#5073b8,
			#1098ad,
			#07b39b,
			#6fba82
		);
		border-radius: 10px;
		z-index: -1;
		animation: animatedgradient 3s ease alternate infinite;
		background-size: 300% 300%;
		filter: blur(4px);
	}

	@keyframes animatedgradient {
		0% {
			background-position: 0% 50%;
		}
		50% {
			background-position: 100% 50%;
		}
		100% {
			background-position: 0% 50%;
		}
	}

	.button-grid-wrapper {
		display: grid;
		grid-template-areas: 'area';
	}

	.big-button {
		padding: 0.5rem 1rem;
		border-radius: 10px;
		cursor: pointer;
		box-shadow:
			0 0 0 1px rgba(0, 0, 0, 0.03),
			0 1px 0 rgba(0, 0, 0, 0.05),
			0 1px 3px rgba(0, 0, 0, 0.1);

		display: inline-block;
	}

	.disabledbutton {
		cursor: not-allowed;
	}

	.big-button:hover {
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
	}

	.big-button-wrapper {
		display: flex;
		justify-content: center;
		align-items: center;
		width: 100%;
		height: 100%;
		grid-area: area;
		opacity: 0;
	}

	.big-button.black {
		color: white;
		background-color: black;
	}

	.big-button.white {
		color: black;
		background-color: white;
	}

	.big-button.pink {
		color: white;
		background-color: #ff7675;
	}

	.big-button.dark-pink {
		color: white;
		background-color: #ad5f5f;
	}

	.big-button.blue {
		color: white;
		background-color: #0984e3;
	}

	.big-button.red {
		color: white;
		background-color: #d63031;
	}

	.big-button.green {
		color: white;
		background-color: #328336;
	}

	.google {
		color: white;
		background-color: #4285f4;
	}

	.button-vanish {
		opacity: 0;
	}

	.button-show {
		opacity: 1;
	}

	.button-slot-wrapper {
		grid-area: area;
		text-align: center;
	}
</style>
