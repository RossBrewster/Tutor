import { useState } from 'react';
import { Question } from './App';

type QuizProps = {
  questions: Question[];
};

export default function Quiz({ questions }: QuizProps) {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answered, setAnswered] = useState<boolean | null>(false);
  const [correct, setCorrect] = useState<boolean | null>(null);


  // Handle when an answer is clicked
  const handleAnswerClick = (answer: string) => {
    if (answer === questions[currentQuestion].correct_answer) {
      console.log('Correct!');
      setAnswered(true);
      setCorrect(true);
    } else {
      console.log('Incorrect!');
        setAnswered(true);
        setCorrect(false);
    }
  };

  const handleNextClick = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion((prev) => prev + 1);
      setAnswered(false);
      setCorrect(null);
    } else {
      console.log('Quiz completed!');
    }
  }

  return (
    <div className="p-4 bg-gray-400 rounded-2xl m-20 w-400px">
      <h1 className="text-black text-xl text-center m-2">
        {questions[currentQuestion].title}
      </h1>
      <h2 className="text-black text-left m-2">
        {questions[currentQuestion].question}
      </h2>

      <div className="flex flex-col space-y-2">
        {!answered && questions[currentQuestion].shuffled_answers.map((answer, index) => (
          <div
            key={index}
            className="bg-blue-200 p-2 rounded-lg text-black cursor-pointer hover:bg-blue-300"
            onClick={() => handleAnswerClick(answer)}
          >
            {answer}
          </div>
        ))}
        {correct && <div className="bg-green-200 p-2 rounded-lg text-black">Correct!</div>}
        {answered && !correct && <div className="bg-red-200 p-2 rounded-lg text-black">Incorrect!</div>}
        {answered && <button className="bg-green-500 p-2 rounded-lg" onClick={handleNextClick}>Next</button>}
      </div>
    </div>
  );
}
