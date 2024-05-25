<script>
	import SketchVideos from '$lib/components/SketchVideos.svelte';
	import RandomDemo from '$lib/components/RandomDemo.svelte';

	import PaperIcon from 'virtual:icons/mingcute/pdf-line';
	import GithubIcon from 'virtual:icons/mdi/github';
	import ArxivIcon from 'virtual:icons/simple-icons/arxiv';
	import UiButton from '../lib/components/UIButton.svelte';
	import LinkButton from '../lib/components/LinkButton.svelte';
</script>

<svelte:head>
	<title>Tree Diffusion</title>
</svelte:head>

<div class="text-lg">
	<div class="flex w-full justify-center font-sans items-end bg-black">
		<div class="mx-8 max-w-3xl w-full text-white pb-12 pt-8 md:pt-28">
			<div
				class="font-sans uppercase text-xs mb-4 tracking-widest text-gray-300 border-1 border border-solid border-gray-300 inline-block px-2 py-1 rounded-md"
			>
				JUNE 2024
			</div>
			<div class="inline-block text-4xl">Diffusion On Syntax Trees For Program Synthesis</div>
			<div class="mt-8 text-lg md:text-xl flex underline text-gray-200 flex-col md:flex-row">
				<div class="hover:text-black hover:bg-white">
					<a href="https://shreyaskapur.com" target="_blank" rel="noreferrer">Shreyas Kapur</a>,
				</div>
				<div class="md:ml-4 hover:text-black hover:bg-white">
					<a href="https://ejenner.com/" target="_blank" rel="noreferrer">Erik Jenner</a>,
				</div>
				<div class="md:ml-4 hover:text-black hover:bg-white">
					<a href="https://people.eecs.berkeley.edu/~russell/" target="_blank" rel="noreferrer"
						>Stuart Russell</a
					>
				</div>
			</div>
			<div class="mt-4 text-gray-300 text-sm">University of California, Berkeley</div>
		</div>
	</div>

	<div class="flex w-full justify-center pt-4 font-sans">
		<div class="mx-8 max-w-3xl w-full">
			<div class="w-full flex justify-center items-center flex-col">
				<div class="flex text-sm md:text-base mb-8 mt-4">
					<LinkButton class="mr-4">
						<div class="flex items-center">
							<PaperIcon class="inline-block mr-1" />
							Paper
						</div>
					</LinkButton>
					<LinkButton class="mr-4">
						<div class="flex items-center">
							<ArxivIcon class="inline-block mr-1" />
							arXiv
						</div>
					</LinkButton>
					<a href="https://github.com/revalo/tree-diffusion">
						<LinkButton>
							<div class="flex items-center">
								<GithubIcon class="inline-block mr-1" />
								Code & Weights
							</div>
						</LinkButton>
					</a>
				</div>
				<div class="pb-4">
					<strong>TLDR;</strong> We teach neural models to *edit* programs, informed by the execution
					output.
				</div>
				<SketchVideos />
			</div>
		</div>
	</div>
	<div class="flex w-full justify-center pt-4 mt-16 font-sans bg-gray-100">
		<div class="mx-8 max-w-3xl w-full">
			<div class="w-full flex justify-center items-center flex-col">
				<div class="font-bold text-center text-xl mt-8">Abstract</div>
				<div class="py-4 mb-8 text-base">
					Large language models generate code one token at a time. Their autoregressive generation
					process lacks the feedback of observing the program's output. Training LLMs to suggest
					edits directly can be challenging due to the scarcity of rich edit data. To address these
					problems, we propose neural diffusion models that operate on syntax trees of any
					context-free grammar. Similar to image diffusion models, our method also inverts <q
						>noise</q
					>
					applied to syntax trees. Rather than generating code sequentially, we iteratively edit it while
					preserving syntactic validity, which makes it easy to combine this neural model with search.
					We apply our approach to inverse graphics tasks, where our model learns to convert images into
					programs that produce those images. Combined with search, our model is able to write graphics
					programs, see the execution result, and debug them to meet the required specifications. We
					additionally show how our system can write graphics programs for hand-drawn sketches.
				</div>
			</div>
		</div>
	</div>
	<div class="flex w-full justify-center pt-4 mt-16 font-sans">
		<div class="mx-8 max-w-3xl w-full">
			<h1 class="mb-8 text-3xl font-bold">What does adding <q>noise</q> mean for programs?</h1>
			<RandomDemo></RandomDemo>
			<div class="mt-4">
				What you're seeing above is our implementation of how we add random mutations to syntax
				trees. We pick random nodes in the syntax tree and replace them with other nodes of the <i
					>correct type</i
				> for the node we're replacing.
			</div>
			<!-- <div class="w-full flex justify-center items-center flex-col h-32"></div> -->
		</div>
	</div>

	<div class="flex w-full justify-center pt-8 font-sans">
		<div class="mx-8 max-w-3xl w-full">
			<h1 class="mb-8 text-3xl font-bold">Tree diffusion lets us use search in program space.</h1>

			<div class="w-full flex items-center justify-center">
				<video src="/videos/search.mp4" autoplay loop muted width="300"></video>
			</div>

			<div class="mt-4">
				Above is a video of our model using search to find the best program to generate given some
				target image. We're not showing all the nodes here, but it does take the model just a few
				layers of search to find the correct program.
			</div>
		</div>
	</div>

	<div class="flex w-full justify-center font-sans mt-16">
		<div class="mx-8 max-w-3xl w-full">
			<h1 class="mb-4 text-3xl font-bold" id="citation">Citation</h1>
			<div
				class="font-mono text-sm mt-4 bg-gray-100 px-4 py-4 border-2 border-solid border-gray-200 rounded-md w-full"
			>
				<pre class="whitespace-pre-wrap">
{`@inproceedings{kapur2024diffusion,
	title = {Diffusion On Syntax Trees For Program Synthesis},
	author = {Kapur, Shreyas and Jenner, Erik and Russell, Stuart},
	booktitle = {arXiv},
	year = {2024},
}`}</pre>
			</div>
			<div class="text-base mt-8">
				We would like to thank Kathy Jang, David Wu, Cam Allen, Sam Toyer, Eli Bronstein, Koushik
				Sen, and Pieter Abbeel for discussions, feedback, and technical support.
			</div>
			<!-- <div class="w-full flex justify-center items-center flex-col h-32"></div> -->
		</div>
	</div>

	<div class="flex w-full justify-center pt-4 mt-16 font-sans bg-gray-100">
		<div class="mx-8 max-w-3xl w-full">
			<div class="w-full flex justify-start items-center flex-col">
				<div class="text-gray-500 mt-4 text-2xl mb-8">
					<a href="#" target="_blank" rel="noreferrer" class="mr-2">
						<PaperIcon class="inline-block hover:text-black" />
					</a>
					<a href="https://github.com/revalo/tree-diffusion" target="_blank" rel="noreferrer">
						<GithubIcon class="inline-block hover:text-black" />
					</a>
				</div>
			</div>
			<div class="text-sm text-gray-600 mb-24">
				This website is licensed under a <a
					class="underline"
					href="http://creativecommons.org/licenses/by-sa/4.0/"
					target="_blank"
					rel="noreferrer">Creative Commons Attribution-ShareAlike 4.0 International License</a
				>. This means you are free to borrow the source code of this website, we just ask that you
				link back to this page in the footer.
			</div>
		</div>
	</div>

	<!-- <div class="flex w-full justify-center pt-4 mt-16 font-sans">
		<div class="mx-8 max-w-3xl w-full">
			<div class="w-full flex justify-center items-center flex-col h-32"></div>
		</div>
	</div> -->
</div>

<style>
	.nice-shadow {
		box-shadow:
			rgba(0, 0, 0, 0.1) 0px 1px 3px 0px,
			rgba(0, 0, 0, 0.06) 0px 1px 2px 0px;
	}
</style>
