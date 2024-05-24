<script>
	import ExpressionPanel from './ExpressionPanel.svelte';
	import ExpressionCode from './ExpressionCode.svelte';
	import UiButton from './UIButton.svelte';
	import UndoIcon from 'virtual:icons/mi/undo';
	import RewindIcon from 'virtual:icons/mdi/rewind';
	import RandomIcon from 'virtual:icons/ion/dice-outline';
	import { loadLang } from '../lang';

	const startingExpression =
		'(- (+ (- (Circle 7 8 8) (Circle 6 8 8)) (Quad 8 8 6 6 H)) (Quad 8 8 A 1 G))';

	let currentExpression = startingExpression;

	let expressionStack = [startingExpression];

	const randomMutate = () => {
		loadLang().then((langLib) => {
			currentExpression = langLib.get_mutated(currentExpression);
			expressionStack = [...expressionStack, currentExpression];
		});
	};

	const reverseNoise = () => {
		if (expressionStack.length > 1) {
			currentExpression = expressionStack[expressionStack.length - 2];
			expressionStack = expressionStack.slice(0, expressionStack.length - 1);
		}
	};

	const resetExpression = () => {
		currentExpression = startingExpression;
		expressionStack = [startingExpression];
	};
</script>

<div class="flex flex-row md:text-lg text-sm">
	<UiButton on:click={resetExpression} color="black" class="mr-2">
		<div class="flex items-center">
			<UndoIcon class="inline-block" />
		</div>
	</UiButton>
	<UiButton on:click={reverseNoise} color="black" class="mr-2">
		<div class="flex items-center">
			<RewindIcon class="inline-block" />
			<span class="ml-1">Reverse Noise</span>
		</div>
	</UiButton>
	<UiButton on:click={randomMutate} color="black gradient-border" class="mr-2">
		<div class="flex items-center">
			<RandomIcon class="inline-block" />
			<span class="ml-1">Add Noise</span>
		</div>
	</UiButton>
</div>
<div class="flex flex-row my-4 overflow-x-clip">
	{#each expressionStack as expression}
		<div class="mr-4 border-2 border-blue-300 border-solid rounded-md p-1">
			<ExpressionPanel size="64" {expression} />
		</div>
	{/each}
</div>

<div class="flex flex-col items-center md:flex-row md:items-start">
	<div>
		<div class="border border-black border-solid inline-block">
			<ExpressionPanel expression={currentExpression} />
		</div>
	</div>
	<div
		class="font-mono text-base mt-4 md:mt-0 bg-gray-100 md:ml-4 px-4 py-4 border-2 border-solid border-gray-200 rounded-md h-72 w-full overflow-y-scroll md:overflow-y-auto"
	>
		<ExpressionCode expression={currentExpression} />
	</div>
</div>
