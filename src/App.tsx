import React from 'react';
import styled from 'styled-components';
import IteratorCanvas from './Components/Views/Iterator/IteratorCanvas';

function App() {
  return (
    <Container>
      <IteratorCanvas/>
    </Container>
  );
}

const Container = styled.div`
  width: 100%;
  height: 100%;
  background: lightgrey;
`

export default App;
