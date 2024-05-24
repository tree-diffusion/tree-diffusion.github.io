<div class="spinner circle fast dark"></div>

<style>
	.circle {
		box-sizing: border-box;
		border-radius: 100%;
		border: 10px solid rgba(0, 0, 0, 0.2);
		width: 20px;
		height: 20px;
		border-width: 3.5px;
	}

	.fast {
		animation: spin 0.7s infinite linear;
	}

	.slow {
		animation: spin 1.8s infinite linear;
	}

	.dark {
		border-top-color: rgba(0, 0, 0, 0.418);
	}

	.light {
		border-top-color: #fff;
	}

	@keyframes spin {
		100% {
			transform: rotate(360deg);
		}
	}
</style>
